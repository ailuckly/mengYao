from sqlite3 import IntegrityError

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from backend.utils.auth import validate_credentials


auth_bp = Blueprint("auth", __name__)


def _users():
    return current_app.extensions["project_services"]["user_repo"]


def _safe_next() -> str:
    next_url = request.args.get("next") or request.form.get("next") or ""
    if next_url.startswith("/") and not next_url.startswith("//"):
        return next_url
    return url_for("main.detect")


@auth_bp.get("/login")
def login():
    if session.get("user_id"):
        return redirect(url_for("main.detect"))
    return render_template("login.html", active_page="login", error="", username="", next_url=_safe_next())


@auth_bp.post("/login")
def login_submit():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    user = _users().verify_credentials(username, password)
    if user is None:
        return render_template(
            "login.html",
            active_page="login",
            error="用户名或密码不正确",
            username=username.strip(),
            next_url=_safe_next(),
        )

    session.clear()
    session["user_id"] = user["id"]
    return redirect(_safe_next())


@auth_bp.get("/register")
def register():
    if session.get("user_id"):
        return redirect(url_for("main.detect"))
    return render_template("register.html", active_page="register", error="", username="")


@auth_bp.post("/register")
def register_submit():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    error = validate_credentials(username, password)
    if error:
        return render_template("register.html", active_page="register", error=error, username=username.strip())

    try:
        user_id = _users().create_user(username, password)
    except IntegrityError:
        return render_template(
            "register.html",
            active_page="register",
            error="用户名已存在",
            username=username.strip(),
        )

    session.clear()
    session["user_id"] = user_id
    return redirect(url_for("main.detect"))


@auth_bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
