from flask import Blueprint, abort, current_app, jsonify, redirect, render_template, request, session, url_for

from backend.utils.auth import login_required
from backend.utils.analysis import load_analysis_summary


main_bp = Blueprint("main", __name__)


def _services() -> dict:
    return current_app.extensions["project_services"]


def _user_id() -> int:
    return int(session["user_id"])


@main_bp.get("/")
def home():
    analysis = load_analysis_summary()
    return render_template("home.html", analysis=analysis, active_page="home")


@main_bp.get("/detect")
@login_required
def detect():
    return render_template("detect.html", active_page="detect")


@main_bp.get("/history")
@login_required
def history():
    label = request.args.get("label") or None
    records = _services()["history_repo"].list_records(user_id=_user_id(), label=label)
    labels = _services()["plant_service"].get_supported_labels()
    return render_template(
        "history.html",
        records=records,
        labels=labels,
        selected_label=label or "",
        active_page="history",
    )


@main_bp.get("/history/<int:record_id>")
@login_required
def history_detail(record_id: int):
    record = _services()["history_repo"].get_record(record_id, user_id=_user_id())
    if record is None:
        abort(404)
    return render_template("history_detail.html", record=record, active_page="history")


@main_bp.post("/history/<int:record_id>/delete")
@login_required
def history_delete(record_id: int):
    deleted = _services()["history_repo"].delete_record(record_id, user_id=_user_id())
    if not deleted:
        abort(404)
    return redirect(url_for("main.history"))


@main_bp.get("/knowledge")
@login_required
def knowledge():
    grouped_items = _services()["knowledge"]
    return render_template("knowledge.html", grouped_items=grouped_items, active_page="knowledge")


@main_bp.get("/analysis")
@login_required
def analysis():
    return render_template("analysis.html", analysis=load_analysis_summary(), active_page="analysis")


@main_bp.get("/api/history")
@login_required
def history_api():
    label = request.args.get("label") or None
    records = _services()["history_repo"].list_records(user_id=_user_id(), label=label)
    return jsonify({"status": "ok", "records": records})


@main_bp.get("/api/history/<int:record_id>")
@login_required
def history_detail_api(record_id: int):
    record = _services()["history_repo"].get_record(record_id, user_id=_user_id())
    if record is None:
        return jsonify({"status": "error", "message": "记录不存在"}), 404
    return jsonify({"status": "ok", "record": record})


@main_bp.get("/api/knowledge")
@login_required
def knowledge_api():
    return jsonify({"status": "ok", "knowledge": _services()["knowledge"]})


@main_bp.get("/api/analysis")
@login_required
def analysis_api():
    return jsonify({"status": "ok", "analysis": load_analysis_summary()})
