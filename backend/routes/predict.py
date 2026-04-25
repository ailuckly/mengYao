import logging

from flask import Blueprint, current_app, jsonify, request, session

from backend.utils.auth import login_required


predict_bp = Blueprint("predict", __name__)
logger = logging.getLogger(__name__)


def _service():
    return current_app.extensions["project_services"]["plant_service"]


@predict_bp.get("/health")
@login_required
def health():
    service = _service()
    return jsonify(
        {
            "status": "ok",
            "message": "service is running",
            "inference_mode": service.get_inference_mode(),
            "model_loaded": service.is_model_loaded(),
        }
    )


@predict_bp.get("/labels")
@login_required
def labels():
    service = _service()
    return jsonify(
        {
            "status": "ok",
            "labels": service.get_supported_labels(),
            "inference_mode": service.get_inference_mode(),
        }
    )


@predict_bp.post("/predict")
@login_required
def predict():
    service = _service()
    file = request.files.get("file")
    if file is None:
        return jsonify({"status": "error", "message": "未接收到图片文件"}), 400

    try:
        result = service.predict(file, user_id=int(session["user_id"]))
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
