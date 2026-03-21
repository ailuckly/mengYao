import json
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDOOR_ROOT = PROJECT_ROOT / "data" / "processed" / "indoor_yolo_v1"
DISEASE_ROOT = PROJECT_ROOT / "data" / "processed" / "plantdoc_disease_v1"
OUTPUT_ROOT = PROJECT_ROOT / "data" / "splits" / "final_v1"
MAPPING_PATH = PROJECT_ROOT / "model" / "configs" / "final_class_mapping.json"
DATASET_YAML = PROJECT_ROOT / "model" / "configs" / "final_dataset_v1.yaml"


def ensure_dirs() -> None:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    for split in ["train", "val", "test"]:
        (OUTPUT_ROOT / split / "images").mkdir(parents=True, exist_ok=True)
        (OUTPUT_ROOT / split / "labels").mkdir(parents=True, exist_ok=True)


def copy_dataset(source_root: Path, prefix: str) -> dict[str, int]:
    stats = {"train": 0, "val": 0, "test": 0}
    for split in stats:
        image_dir = source_root / split / "images"
        label_dir = source_root / split / "labels"
        if not image_dir.exists() or not label_dir.exists():
            continue

        for label_path in sorted(label_dir.glob("*.txt")):
            image_candidates = list(image_dir.glob(f"{label_path.stem}.*"))
            if not image_candidates:
                continue

            image_path = image_candidates[0]
            new_stem = f"{prefix}_{label_path.stem}"
            dst_image = OUTPUT_ROOT / split / "images" / f"{new_stem}{image_path.suffix.lower()}"
            dst_label = OUTPUT_ROOT / split / "labels" / f"{new_stem}.txt"
            shutil.copy2(image_path, dst_image)
            shutil.copy2(label_path, dst_label)
            stats[split] += 1
    return stats


def write_dataset_yaml() -> None:
    config = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    class_names = config["target_classes"]
    lines = [
        "path: ../../data/splits/final_v1",
        "train: train/images",
        "val: val/images",
        "test: test/images",
        "",
        "names:",
    ]
    for key, value in class_names.items():
        lines.append(f"  {key}: {value}")
    DATASET_YAML.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    indoor_stats = copy_dataset(INDOOR_ROOT, "indoor")
    disease_stats = copy_dataset(DISEASE_ROOT, "disease")
    write_dataset_yaml()
    summary = {
        "indoor": indoor_stats,
        "disease": disease_stats,
        "output": str(OUTPUT_ROOT),
        "dataset_yaml": str(DATASET_YAML),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
