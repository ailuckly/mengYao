from datetime import datetime

from werkzeug.datastructures import FileStorage

from backend.config import DEFAULT_MODEL_PATH
from backend.inference.predictor import YOLOPredictor
from backend.utils.history import HistoryRepository
from backend.utils.advice import get_advice, load_label_map
from backend.utils.files import save_upload_file


class PlantRecognitionService:
    def __init__(self, history_repo: HistoryRepository) -> None:
        self.label_map = load_label_map()
        self.history_repo = history_repo
        self.predictor = YOLOPredictor(
            model_path=DEFAULT_MODEL_PATH,
            label_map=self.label_map,
        )

    def get_supported_labels(self) -> list[str]:
        return list(self.label_map.values())

    def get_inference_mode(self) -> str:
        return self.predictor.mode

    def is_model_loaded(self) -> bool:
        return self.predictor.model is not None

    def predict(self, file: FileStorage) -> dict:
        upload_path = save_upload_file(file)
        predictions = self.predictor.predict(upload_path)
        labels = [item["label"] for item in predictions]
        advices = [get_advice(label) for label in labels]
        top_label = labels[0] if labels else "未识别"
        top_score = float(predictions[0]["score"]) if predictions else 0.0
        upload_image = f"/records/uploads/{upload_path.name}"
        result_image = predictions[0]["result_image"] if predictions else ""

        record_id = self.history_repo.add_record(
            {
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "image_name": upload_path.name,
                "upload_image": upload_image,
                "result_image": result_image,
                "top_label": top_label,
                "top_score": top_score,
                "prediction_count": len(predictions),
                "inference_mode": self.get_inference_mode(),
                "predictions": predictions,
                "advice": advices,
            }
        )

        return {
            "status": "ok",
            "message": "识别完成",
            "record_id": record_id,
            "image_name": upload_path.name,
            "upload_image": upload_image,
            "labels": labels,
            "scores": [item["score"] for item in predictions],
            "boxes": [item["box"] for item in predictions],
            "advice": advices,
            "result_image": result_image,
            "predictions": predictions,
            "meta": {
                "inference_mode": self.get_inference_mode(),
                "prediction_count": len(predictions),
                "model_loaded": self.is_model_loaded(),
            },
        }
