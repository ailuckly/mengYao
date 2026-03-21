import logging

from flask import Blueprint, jsonify, request

from backend.services.plant_service import PlantRecognitionService


predict_bp = Blueprint("predict", __name__)
service = PlantRecognitionService()
logger = logging.getLogger(__name__)


@predict_bp.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "message": "service is running",
            "inference_mode": service.get_inference_mode(),
            "model_loaded": service.is_model_loaded(),
        }
    )


@predict_bp.get("/labels")
def labels():
    return jsonify(
        {
            "status": "ok",
            "labels": service.get_supported_labels(),
            "inference_mode": service.get_inference_mode(),
        }
    )


@predict_bp.post("/predict")
def predict():
    file = request.files.get("file")
    if file is None:
        return jsonify({"status": "error", "message": "未接收到图片文件"}), 400

    try:
        result = service.predict(file)
    except ValueError as exc:
        logger.warning("invalid request: %s", exc)
        return jsonify({"status": "error", "message": str(exc)}), 400
    except RuntimeError as exc:
        logger.exception("prediction failed")
        return jsonify({"status": "error", "message": str(exc)}), 500

    logger.info(
        "prediction finished: mode=%s labels=%s",
        result["meta"]["inference_mode"],
        ",".join(result["labels"]),
    )
    return jsonify(result)
