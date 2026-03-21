import json
import random
import shutil
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PROJECT_ROOT / "data" / "raw" / "public" / "indoor_augmented_plants" / "Augmented Data"
OUTPUT_ROOT = PROJECT_ROOT / "data" / "processed" / "indoor_yolo_v1"
MAPPING_PATH = PROJECT_ROOT / "model" / "configs" / "final_class_mapping.json"
SEED = 42
SPLITS = {"train": 0.8, "val": 0.1, "test": 0.1}


def load_mapping() -> dict[str, int]:
    data = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    return data["indoor_mapping"]


def decide_split(index: int, total: int) -> str:
    train_cut = int(total * SPLITS["train"])
    val_cut = train_cut + int(total * SPLITS["val"])
    if index < train_cut:
        return "train"
    if index < val_cut:
        return "val"
    return "test"


def ensure_dirs() -> None:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    for split in SPLITS:
        (OUTPUT_ROOT / split / "images").mkdir(parents=True, exist_ok=True)
        (OUTPUT_ROOT / split / "labels").mkdir(parents=True, exist_ok=True)


def write_label(path: Path, class_id: int) -> None:
    path.write_text(f"{class_id} 0.5 0.5 1.0 1.0\n", encoding="utf-8")


def main() -> None:
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"source folder not found: {SOURCE_ROOT}")

    ensure_dirs()
    mapping = load_mapping()
    random.seed(SEED)
    summary: dict[str, int] = {}

    for folder_name, class_id in mapping.items():
        class_dir = SOURCE_ROOT / folder_name
        if not class_dir.exists():
            continue

        files = [p for p in class_dir.iterdir() if p.is_file()]
        random.shuffle(files)
        summary[folder_name] = len(files)

        for index, image_path in enumerate(files):
            try:
                with Image.open(image_path) as image:
                    image.verify()
            except Exception:
                continue

            split = decide_split(index, len(files))
            target_stem = f"{folder_name.lower().replace(' ', '_')}_{index:05d}"
            target_image = OUTPUT_ROOT / split / "images" / f"{target_stem}{image_path.suffix.lower()}"
            target_label = OUTPUT_ROOT / split / "labels" / f"{target_stem}.txt"
            shutil.copy2(image_path, target_image)
            write_label(target_label, class_id)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
