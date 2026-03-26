import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from backend.app import create_app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test_app.db"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE_PATH": str(db_path),
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _make_image(self) -> io.BytesIO:
        buffer = io.BytesIO()
        image = Image.new("RGB", (160, 120), color=(120, 180, 90))
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    def test_main_pages_render(self):
        for path in ["/", "/detect", "/history", "/knowledge", "/analysis"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)

    def test_health_and_labels_endpoints(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("inference_mode", data)

        response = self.client.get("/labels")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["labels"])

        knowledge_response = self.client.get("/api/knowledge")
        self.assertEqual(knowledge_response.status_code, 200)
        knowledge_data = knowledge_response.get_json()
        self.assertEqual(knowledge_data["status"], "ok")
        self.assertTrue(knowledge_data["knowledge"]["plant"])
        self.assertTrue(knowledge_data["knowledge"]["disease"])

        analysis_response = self.client.get("/api/analysis")
        self.assertEqual(analysis_response.status_code, 200)
        analysis_data = analysis_response.get_json()
        self.assertEqual(analysis_data["status"], "ok")
        self.assertIn("metrics", analysis_data["analysis"])
        self.assertIn("artifact_exists", analysis_data["analysis"])
        self.assertEqual(analysis_data["analysis"]["class_count"], 10)

    def test_predict_creates_history_record(self):
        response = self.client.post(
            "/predict",
            data={"file": (self._make_image(), "plant.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("record_id", data)
        self.assertIn("meta", data)
        self.assertTrue(data["predictions"])

        record_id = data["record_id"]

        history_response = self.client.get("/api/history")
        history_data = history_response.get_json()
        self.assertEqual(history_response.status_code, 200)
        self.assertEqual(history_data["status"], "ok")
        self.assertEqual(len(history_data["records"]), 1)
        self.assertEqual(history_data["records"][0]["id"], record_id)

        detail_response = self.client.get(f"/api/history/{record_id}")
        detail_data = detail_response.get_json()
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_data["status"], "ok")
        self.assertEqual(detail_data["record"]["id"], record_id)
        self.assertTrue(detail_data["record"]["predictions"])

    def test_history_detail_missing_record(self):
        response = self.client.get("/history/9999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("未找到对应页面", response.get_data(as_text=True))

        api_response = self.client.get("/api/history/9999")
        self.assertEqual(api_response.status_code, 404)
        self.assertEqual(api_response.get_json()["status"], "error")

    def test_history_delete_endpoint(self):
        response = self.client.post(
            "/predict",
            data={"file": (self._make_image(), "delete.png")},
            content_type="multipart/form-data",
        )
        record_id = response.get_json()["record_id"]

        delete_response = self.client.post(f"/history/{record_id}/delete")
        self.assertEqual(delete_response.status_code, 302)

        history_response = self.client.get("/api/history")
        history_data = history_response.get_json()
        self.assertEqual(history_data["records"], [])

    def test_predict_endpoint_with_invalid_extension(self):
        response = self.client.post(
            "/predict",
            data={"file": (io.BytesIO(b"plain-text"), "bad.txt")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["status"], "error")


if __name__ == "__main__":
    unittest.main()
