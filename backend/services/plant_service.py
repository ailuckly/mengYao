from werkzeug.datastructures import FileStorage

from backend.config import DEFAULT_MODEL_PATH
from backend.inference.predictor import YOLOPredictor
from backend.utils.advice import get_advice, load_label_map
from backend.utils.files import save_upload_file

class PlantRecognitionService:
    def __init__(self) -> None:
        self.label_map = load_label_map()
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

        return {
            "status": "ok",
            "message": "识别完成",
            "image_name": upload_path.name,
            "labels": labels,
            "scores": [item["score"] for item in predictions],
            "boxes": [item["box"] for item in predictions],
            "advice": advices,
            "result_image": predictions[0]["result_image"] if predictions else "",
            "predictions": predictions,
            "meta": {
                "inference_mode": self.get_inference_mode(),
                "prediction_count": len(predictions),
                "model_loaded": self.is_model_loaded(),
            },
        }
