import json
import sqlite3
from pathlib import Path
from typing import Any


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS prediction_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    image_name TEXT NOT NULL,
    upload_image TEXT NOT NULL,
    result_image TEXT NOT NULL,
    top_label TEXT NOT NULL,
    top_score REAL NOT NULL,
    prediction_count INTEGER NOT NULL,
    inference_mode TEXT NOT NULL,
    predictions_json TEXT NOT NULL,
    advice_json TEXT NOT NULL
);
"""


class HistoryRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(SCHEMA_SQL)
            conn.commit()

    def add_record(self, payload: dict[str, Any]) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO prediction_records (
                    created_at,
                    image_name,
                    upload_image,
                    result_image,
                    top_label,
                    top_score,
                    prediction_count,
                    inference_mode,
                    predictions_json,
                    advice_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["created_at"],
                    payload["image_name"],
                    payload["upload_image"],
                    payload["result_image"],
                    payload["top_label"],
                    payload["top_score"],
                    payload["prediction_count"],
                    payload["inference_mode"],
                    json.dumps(payload["predictions"], ensure_ascii=False),
                    json.dumps(payload["advice"], ensure_ascii=False),
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def list_records(self, label: str | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT *
            FROM prediction_records
        """
        params: tuple[Any, ...] = ()
        if label:
            query += " WHERE top_label = ?"
            params = (label,)
        query += " ORDER BY id DESC"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
        return [self._serialize_summary(dict(row)) for row in rows]

    def get_record(self, record_id: int) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM prediction_records WHERE id = ?",
                (record_id,),
            ).fetchone()
        if row is None:
            return None
        return self._serialize_detail(dict(row))

    def delete_record(self, record_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM prediction_records WHERE id = ?",
                (record_id,),
            )
            conn.commit()
        return cursor.rowcount > 0

    def _serialize_summary(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "image_name": row["image_name"],
            "upload_image": row["upload_image"],
            "result_image": row["result_image"],
            "top_label": row["top_label"],
            "top_score": row["top_score"],
            "prediction_count": row["prediction_count"],
            "inference_mode": row["inference_mode"],
        }

    def _serialize_detail(self, row: dict[str, Any]) -> dict[str, Any]:
        item = self._serialize_summary(row)
        item["predictions"] = json.loads(row["predictions_json"])
        item["advice"] = json.loads(row["advice_json"])
        return item
