from flask import Flask, render_template, send_from_directory

from backend.config import (
    FRONTEND_DIR,
    LOG_DIR,
    MAX_CONTENT_LENGTH,
    PREDICTION_DIR,
    PROJECT_ROOT,
    RECORDS_DIR,
    UPLOAD_DIR,
)
from backend.routes.predict import predict_bp
from backend.utils.logging_utils import configure_logging


def create_app() -> Flask:
    configure_logging(LOG_DIR)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    PREDICTION_DIR.mkdir(parents=True, exist_ok=True)

    app = Flask(
        __name__,
        template_folder=str(FRONTEND_DIR / "templates"),
        static_folder=str(FRONTEND_DIR / "static"),
    )
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    app.register_blueprint(predict_bp)

    @app.get("/")
    def index():
        return render_template("index.html", project_root=PROJECT_ROOT.name)

    @app.get("/records/<path:filename>")
    def serve_record(filename: str):
        return send_from_directory(RECORDS_DIR, filename)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
