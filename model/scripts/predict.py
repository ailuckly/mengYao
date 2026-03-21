import argparse
import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WEIGHTS = PROJECT_ROOT / "model" / "checkpoints" / "best.pt"
DEFAULT_OUTPUT = PROJECT_ROOT / "records" / "logs" / "predict_last_run.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run YOLOv11 prediction from CLI.")
    parser.add_argument("--source", required=True, help="image path or directory")
    parser.add_argument("--weights", default=str(DEFAULT_WEIGHTS), help="weights path")
    parser.add_argument("--conf", type=float, default=0.25, help="confidence threshold")
    parser.add_argument("--save", action="store_true", help="save plotted image results")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="json summary output path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = Path(args.source).resolve()
    weights_path = Path(args.weights).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"source not found: {source_path}")
    if not weights_path.exists():
        raise FileNotFoundError(f"weights not found: {weights_path}")

    try:
        from ultralytics import YOLO
    except Exception as exc:
        raise RuntimeError("ultralytics 未安装，无法执行预测。") from exc

    model = YOLO(str(weights_path))
    results = model.predict(source=str(source_path), conf=args.conf, save=args.save)
    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source": str(source_path),
        "weights": str(weights_path),
        "conf": args.conf,
        "save": args.save,
        "result_count": len(results),
    }

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
