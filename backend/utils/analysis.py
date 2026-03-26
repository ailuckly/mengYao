import json

from backend.config import ANALYSIS_IMAGE_DIR, LABEL_CONFIG_PATH, TRAINING_SUMMARY_PATH


def load_analysis_summary() -> dict:
    summary = {
        "run_name": "colab_pro_formal_v13",
        "model": "YOLOv11s",
        "best_epoch": 83,
        "metrics": {
            "precision": 0.7441,
            "recall": 0.7495,
            "map50": 0.7279,
            "map50_95": 0.6754,
        },
        "artifact_urls": {
            "results_plot": "/static/images/analysis/results.png",
            "confusion_matrix": "/static/images/analysis/confusion_matrix_normalized.png",
        },
        "artifact_exists": {
            "results_plot": False,
            "confusion_matrix": False,
        },
        "class_count": 0,
        "labels": [],
    }

    if TRAINING_SUMMARY_PATH.exists():
        with TRAINING_SUMMARY_PATH.open("r", encoding="utf-8") as file:
            summary.update(json.load(file))

    if LABEL_CONFIG_PATH.exists():
        with LABEL_CONFIG_PATH.open("r", encoding="utf-8") as file:
            labels = list(json.load(file).get("labels", {}).values())
            summary["labels"] = labels
            summary["class_count"] = len(labels)

    metrics = summary.get("metrics", {})
    summary["metrics"] = {
        "precision": float(metrics.get("precision", 0.0)),
        "recall": float(metrics.get("recall", 0.0)),
        "map50": float(metrics.get("map50", 0.0)),
        "map50_95": float(metrics.get("map50_95", 0.0)),
    }

    summary["artifact_exists"] = {
        "results_plot": (ANALYSIS_IMAGE_DIR / "results.png").exists(),
        "confusion_matrix": (ANALYSIS_IMAGE_DIR / "confusion_matrix_normalized.png").exists(),
    }

    return summary
