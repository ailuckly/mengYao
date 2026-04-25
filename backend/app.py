import os
import secrets
from pathlib import Path

from flask import Flask, abort, render_template, send_from_directory, session

from backend.config import (
    DATABASE_PATH,
    FRONTEND_DIR,
    LOG_DIR,
    MAX_CONTENT_LENGTH,
    PREDICTION_DIR,
    RECORDS_DIR,
    UPLOAD_DIR,
)
from backend.routes.auth import auth_bp
from backend.routes.main import main_bp
from backend.routes.predict import predict_bp
from backend.services.plant_service import PlantRecognitionService
from backend.utils.auth import UserRepository, login_required
from backend.utils.history import HistoryRepository
from backend.utils.knowledge import group_knowledge_items, load_knowledge_items
from backend.utils.logging_utils import configure_logging


def create_app(test_config: dict | None = None) -> Flask:
    configure_logging(LOG_DIR)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    PREDICTION_DIR.mkdir(parents=True, exist_ok=True)

    app = Flask(
        __name__,
        template_folder=str(FRONTEND_DIR / "templates"),
        static_folder=str(FRONTEND_DIR / "static"),
    )
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    app.config["DATABASE_PATH"] = str(DATABASE_PATH)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    if test_config:
        app.config.update(test_config)

    history_repo = HistoryRepository(db_path=Path(app.config["DATABASE_PATH"]))
    user_repo = UserRepository(db_path=Path(app.config["DATABASE_PATH"]))
    history_repo.init_db()
    user_repo.init_db()

    app.extensions["project_services"] = {
        "history_repo": history_repo,
        "user_repo": user_repo,
        "plant_service": PlantRecognitionService(history_repo=history_repo),
        "knowledge": group_knowledge_items(load_knowledge_items()),
    }

    @app.context_processor
    def inject_current_user():
        from flask import session

        user_id = session.get("user_id")
        current_user = user_repo.get_by_id(user_id) if user_id else None
        return {"current_user": current_user}

    app.register_blueprint(auth_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(main_bp)

    @app.get("/records/<path:filename>")
    @login_required
    def serve_record(filename: str):
        record_url = f"/records/{filename}"
        if not history_repo.user_owns_file(int(session["user_id"]), record_url):
            abort(404)
        return send_from_directory(RECORDS_DIR, filename)

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html", active_page=""), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
