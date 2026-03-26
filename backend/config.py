from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
RECORDS_DIR = PROJECT_ROOT / "records"
UPLOAD_DIR = RECORDS_DIR / "uploads"
PREDICTION_DIR = RECORDS_DIR / "predictions"
LOG_DIR = RECORDS_DIR / "logs"
DATABASE_PATH = RECORDS_DIR / "app.db"
MODEL_DIR = PROJECT_ROOT / "model"
DEFAULT_MODEL_PATH = MODEL_DIR / "checkpoints" / "best.pt"
LABEL_CONFIG_PATH = MODEL_DIR / "configs" / "label_advice.json"
TRAINING_SUMMARY_PATH = MODEL_DIR / "configs" / "training_summary.json"
ANALYSIS_IMAGE_DIR = FRONTEND_DIR / "static" / "images" / "analysis"

MAX_CONTENT_LENGTH = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
