from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = PROJECT_ROOT / "data" / "splits" / "final_v1"
DATASET_YAML = PROJECT_ROOT / "model" / "configs" / "final_dataset_v1.yaml"
OUTPUT_ZIP = PROJECT_ROOT / "model" / "exports" / "colab" / "final_dataset_v1_bundle.zip"


def main() -> None:
    if not DATASET_ROOT.exists():
        raise FileNotFoundError(f"dataset not found: {DATASET_ROOT}")
    if not DATASET_YAML.exists():
        raise FileNotFoundError(f"dataset yaml not found: {DATASET_YAML}")

    OUTPUT_ZIP.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT_ZIP, "w", compression=ZIP_DEFLATED) as archive:
        archive.write(DATASET_YAML, DATASET_YAML.relative_to(PROJECT_ROOT))
        for path in DATASET_ROOT.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(PROJECT_ROOT))
    print(f"dataset bundle created: {OUTPUT_ZIP}")


if __name__ == "__main__":
    main()
