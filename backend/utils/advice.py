import json

from backend.config import LABEL_CONFIG_PATH

DEFAULT_CONFIG = {
    "labels": {
        "0": "绿萝",
        "1": "吊兰",
        "2": "多肉",
        "3": "月季",
        "4": "兰花",
        "5": "叶斑病",
        "6": "黄化症状",
    },
    "advice": {
        "绿萝": "保持散射光环境，盆土见干见湿，注意通风。",
        "吊兰": "避免强光直晒，适量浇水，定期修剪枯叶。",
        "多肉": "控制浇水频率，保持充足光照，防止积水烂根。",
        "月季": "保证光照和通风，及时修剪枯枝，注意病虫害观察。",
        "兰花": "保持湿润和通风，避免暴晒，控制浇水量。",
        "叶斑病": "减少叶面长期潮湿，观察病斑扩散情况，必要时隔离病株。",
        "黄化症状": "检查浇水、施肥和光照条件，排查缺素或积水问题。",
    },
}


def _load_config() -> dict:
    if LABEL_CONFIG_PATH.exists():
        with LABEL_CONFIG_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)
    return DEFAULT_CONFIG


def load_label_map() -> dict[int, str]:
    labels = _load_config().get("labels", {})
    return {int(key): value for key, value in labels.items()}


def get_advice(label: str) -> str:
    advice = _load_config().get("advice", {})
    return advice.get(label, "请结合植物状态进一步观察，并在必要时人工复核。")
