import json
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PROJECT_ROOT / "data" / "raw" / "public" / "plantdoc_yolo_v2_100x100"
OUTPUT_ROOT = PROJECT_ROOT / "data" / "processed" / "plantdoc_disease_v1"
MAPPING_PATH = PROJECT_ROOT / "model" / "configs" / "final_class_mapping.json"
SOURCE_NAMES = [
    "Apple Scab Leaf",
    "Apple leaf",
    "Apple rust leaf",
    "Bell_pepper leaf",
    "Bell_pepper leaf spot",
    "Blueberry leaf",
    "Cherry leaf",
    "Corn Gray leaf spot",
    "Corn leaf blight",
    "Corn rust leaf",
    "Peach leaf",
    "Potato leaf",
    "Potato leaf early blight",
    "Potato leaf late blight",
    "Raspberry leaf",
    "Soyabean leaf",
    "Soybean leaf",
    "Squash Powdery mildew leaf",
    "Strawberry leaf",
    "Tomato Early blight leaf",
    "Tomato Septoria leaf spot",
    "Tomato leaf",
    "Tomato leaf bacterial spot",
    "Tomato leaf late blight",
    "Tomato leaf mosaic virus",
    "Tomato leaf yellow virus",
    "Tomato mold leaf",
    "Tomato two spotted spider mites leaf",
    "grape leaf",
    "grape leaf black rot",
]


def load_mapping() -> dict[int, int]:
    config = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    source_mapping = config["plantdoc_disease_mapping"]
    return {SOURCE_NAMES.index(name): target for name, target in source_mapping.items()}


def ensure_dirs() -> None:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    for split in ["train", "val", "test"]:
        (OUTPUT_ROOT / split / "images").mkdir(parents=True, exist_ok=True)
        (OUTPUT_ROOT / split / "labels").mkdir(parents=True, exist_ok=True)


def remap_label_file(src_label: Path, dst_label: Path, class_mapping: dict[int, int]) -> bool:
    kept_lines = []
    for line in src_label.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        source_class = int(parts[0])
        if source_class not in class_mapping:
            continue
        parts[0] = str(class_mapping[source_class])
        kept_lines.append(" ".join(parts))

    if not kept_lines:
        return False

    dst_label.write_text("\n".join(kept_lines) + "\n", encoding="utf-8")
    return True


def copy_split(source_split: str, target_split: str, class_mapping: dict[int, int]) -> int:
    image_dir = SOURCE_ROOT / source_split / "images"
    label_dir = SOURCE_ROOT / source_split / "labels"
    if not image_dir.exists() or not label_dir.exists():
        return 0

    count = 0
    for label_path in sorted(label_dir.glob("*.txt")):
        image_candidates = list(image_dir.glob(f"{label_path.stem}.*"))
        if not image_candidates:
            continue

        dst_label = OUTPUT_ROOT / target_split / "labels" / label_path.name
        keep = remap_label_file(label_path, dst_label, class_mapping)
        if not keep:
            continue

        image_path = image_candidates[0]
        dst_image = OUTPUT_ROOT / target_split / "images" / image_path.name
        shutil.copy2(image_path, dst_image)
        count += 1
    return count


def split_train_to_val(class_mapping: dict[int, int]) -> tuple[int, int]:
    image_dir = SOURCE_ROOT / "train" / "images"
    label_dir = SOURCE_ROOT / "train" / "labels"
    label_paths = sorted(label_dir.glob("*.txt"))
    train_count = 0
    val_count = 0

    for index, label_path in enumerate(label_paths):
        image_candidates = list(image_dir.glob(f"{label_path.stem}.*"))
        if not image_candidates:
            continue

        target_split = "val" if index % 10 == 0 else "train"
        dst_label = OUTPUT_ROOT / target_split / "labels" / label_path.name
        keep = remap_label_file(label_path, dst_label, class_mapping)
        if not keep:
            continue

        image_path = image_candidates[0]
        dst_image = OUTPUT_ROOT / target_split / "images" / image_path.name
        shutil.copy2(image_path, dst_image)
        if target_split == "val":
            val_count += 1
        else:
            train_count += 1

    return train_count, val_count


def main() -> None:
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"source folder not found: {SOURCE_ROOT}")

    ensure_dirs()
    class_mapping = load_mapping()
    train_count, val_count = split_train_to_val(class_mapping)
    test_count = copy_split("test", "test", class_mapping)
    summary = {
        "train": train_count,
        "val": val_count,
        "test": test_count,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
