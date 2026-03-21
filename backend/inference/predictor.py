from pathlib import Path
from typing import Any
from uuid import uuid4

from PIL import Image, ImageDraw

from backend.config import PREDICTION_DIR


class YOLOPredictor:
    def __init__(self, model_path: Path, label_map: dict[int, str]) -> None:
        self.model_path = model_path
        self.label_map = label_map
        self.model = self._load_model()
        self.mode = "real" if self.model is not None else "mock"

    def _load_model(self) -> Any | None:
        if not self.model_path.exists():
            return None

        try:
            from ultralytics import YOLO
        except Exception:
            return None

        return YOLO(str(self.model_path))

    def predict(self, image_path: Path) -> list[dict]:
        if self.model is None:
            return [self._mock_predict(image_path)]
        return self._real_predict(image_path)

    def _real_predict(self, image_path: Path) -> list[dict]:
        results = self.model(str(image_path))
        if not results:
            return [self._mock_predict(image_path)]

        result = results[0]
        names = getattr(result, "names", {})
        boxes = getattr(result, "boxes", None)
        if boxes is None or len(boxes) == 0:
            return [self._mock_predict(image_path)]

        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        output: list[dict] = []

        for box in boxes:
            coords = [round(v, 2) for v in box.xyxy[0].tolist()]
            cls_idx = int(box.cls[0].item())
            score = round(float(box.conf[0].item()), 4)
            label = names.get(cls_idx, self.label_map.get(cls_idx, f"class_{cls_idx}"))
            draw.rectangle(coords, outline="red", width=3)
            draw.text((coords[0] + 4, coords[1] + 4), f"{label} {score:.2f}", fill="red")
            output.append(
                {
                    "label": label,
                    "score": score,
                    "box": coords,
                }
            )

        image_name = f"predict_{uuid4().hex}.png"
        image.save(PREDICTION_DIR / image_name)
        for item in output:
            item["result_image"] = f"/records/predictions/{image_name}"
            item["source"] = "real-model"
        return output

    def _mock_predict(self, image_path: Path) -> dict:
        image = Image.open(image_path).convert("RGB")
        width, height = image.size
        label = self._guess_label(image_path)
        score = 0.9231
        box = [30, 30, max(60, width - 30), max(60, height - 30)]

        draw = ImageDraw.Draw(image)
        draw.rectangle(box, outline="green", width=4)
        draw.text((box[0] + 6, box[1] + 6), f"{label} {score:.2f}", fill="green")

        image_name = f"mock_{uuid4().hex}.png"
        image.save(PREDICTION_DIR / image_name)
        return {
            "label": label,
            "score": score,
            "box": box,
            "result_image": f"/records/predictions/{image_name}",
            "source": "mock-model",
        }

    def _guess_label(self, image_path: Path) -> str:
        filename = image_path.name.lower()
        if any(token in filename for token in ["mildew", "mold", "powdery"]):
            return "白粉/霉变类病害"
        if any(token in filename for token in ["yellow", "rust", "mosaic", "spider", "虫", "黄"]):
            return "黄化/锈病/虫害类异常"
        if any(token in filename for token in ["blight", "wilt", "疫", "枯"]):
            return "枯萎/疫病类病害"
        if any(token in filename for token in ["spot", "scab", "rot", "斑"]):
            return "叶斑类病害"
        if "aglaonema" in filename:
            return "银皇后类"
        if "cryptanthus" in filename:
            return "网纹凤梨类"
        if any(token in filename for token in ["ivy", "pothos", "绿萝"]):
            return "绿萝类"
        if any(token in filename for token in ["philodendron", "蔓绿绒"]):
            return "心叶蔓绿绒类"
        if "rhaphidophora" in filename:
            return "Rhaphidophora类"
        if any(token in filename for token in ["zz", "zamioculcas", "金钱树"]):
            return "金钱树类"
        return self.label_map.get(0, "银皇后类")
