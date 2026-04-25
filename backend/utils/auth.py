import sqlite3
from functools import wraps
from pathlib import Path
from typing import Any

from flask import current_app, jsonify, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


USER_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class UserRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(USER_SCHEMA_SQL)
            conn.commit()

    def create_user(self, username: str, password: str) -> int:
        normalized = normalize_username(username)
        password_hash = generate_password_hash(password)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (normalized, password_hash),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_by_username(self, username: str) -> dict[str, Any] | None:
        normalized = normalize_username(username)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (normalized,),
            ).fetchone()
        return dict(row) if row else None

    def get_by_id(self, user_id: int) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT id, username FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return dict(row) if row else None

    def verify_credentials(self, username: str, password: str) -> dict[str, Any] | None:
        user = self.get_by_username(username)
        if user is None:
            return None
        if not check_password_hash(user["password_hash"], password):
            return None
        return {"id": user["id"], "username": user["username"]}


def normalize_username(username: str) -> str:
    return username.strip().lower()


def validate_credentials(username: str, password: str) -> str | None:
    if not normalize_username(username):
        return "请输入用户名"
    if len(normalize_username(username)) < 3:
        return "用户名至少需要 3 个字符"
    if len(password) < 6:
        return "密码至少需要 6 个字符"
    return None


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id:
            user_repo = current_app.extensions["project_services"]["user_repo"]
            if user_repo.get_by_id(user_id) is not None:
                return view(*args, **kwargs)
            session.clear()

        if request.path.startswith("/api/") or request.blueprint == "predict":
            return jsonify({"status": "error", "message": "请先登录"}), 401
        return redirect(url_for("auth.login", next=request.path))

    return wrapped_view
