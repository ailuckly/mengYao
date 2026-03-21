import io
import unittest

from PIL import Image

from backend.app import create_app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def _make_image(self) -> io.BytesIO:
        buffer = io.BytesIO()
        image = Image.new("RGB", (160, 120), color=(120, 180, 90))
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("inference_mode", data)

    def test_labels_endpoint(self):
        response = self.client.get("/labels")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["labels"])

    def test_predict_endpoint_with_valid_image(self):
        response = self.client.post(
            "/predict",
            data={"file": (self._make_image(), "plant.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("meta", data)
        self.assertTrue(data["predictions"])

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
