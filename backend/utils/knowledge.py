import json
from collections.abc import Iterable

from backend.config import LABEL_CONFIG_PATH


def load_knowledge_items() -> list[dict]:
    if not LABEL_CONFIG_PATH.exists():
        return []

    with LABEL_CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = json.load(file)

    knowledge = config.get("knowledge", {})
    items = []
    for label in config.get("labels", {}).values():
        item = knowledge.get(label)
        if not item:
            continue
        items.append({"label": label, **item})
    return items


def group_knowledge_items(items: Iterable[dict]) -> dict[str, list[dict]]:
    plants: list[dict] = []
    diseases: list[dict] = []

    for item in items:
        if item.get("category_type") == "plant":
            plants.append(item)
        else:
            diseases.append(item)

    return {"plant": plants, "disease": diseases}
