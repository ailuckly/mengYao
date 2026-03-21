from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ZIP = PROJECT_ROOT / "model" / "exports" / "colab" / "project_bundle.zip"
INCLUDE_PATHS = [
    "backend",
    "frontend",
    "model",
    "requirements.txt",
    "README.md",
]
SKIP_PARTS = {"__pycache__", "checkpoints", "exports"}
SKIP_SUFFIXES = {".pyc"}


def iter_files(base: Path):
    if base.is_file():
        yield base
        return

    for path in base.rglob("*"):
        if path.is_dir():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix in SKIP_SUFFIXES:
            continue
        yield path


def main() -> None:
    OUTPUT_ZIP.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT_ZIP, "w", compression=ZIP_DEFLATED) as archive:
        for relative in INCLUDE_PATHS:
            base = PROJECT_ROOT / relative
            if not base.exists():
                continue
            for file_path in iter_files(base):
                archive.write(file_path, file_path.relative_to(PROJECT_ROOT))
    print(f"project bundle created: {OUTPUT_ZIP}")


if __name__ == "__main__":
    main()
