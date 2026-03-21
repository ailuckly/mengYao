import argparse
import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = PROJECT_ROOT / "model" / "configs" / "final_dataset_v1.yaml"
DEFAULT_WEIGHTS = "yolo11n.pt"
RUN_LOG_PATH = PROJECT_ROOT / "records" / "logs" / "training_last_run.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLOv11 for plant recognition.")
    parser.add_argument("--data", default=str(DEFAULT_DATASET), help="dataset yaml path")
    parser.add_argument("--weights", default=DEFAULT_WEIGHTS, help="base model weights")
    parser.add_argument("--imgsz", type=int, default=640, help="image size")
    parser.add_argument("--epochs", type=int, default=100, help="training epochs")
    parser.add_argument("--batch", type=int, default=16, help="batch size")
    parser.add_argument("--device", default="0", help="cuda device id or cpu")
    parser.add_argument("--project", default="model/exports/train_runs", help="training output dir")
    parser.add_argument("--name", default="plant_yolo11_baseline", help="run name")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.data).resolve()
    if not dataset_path.exists():
        raise FileNotFoundError(f"dataset yaml not found: {dataset_path}")

    try:
        from ultralytics import YOLO
    except Exception as exc:
        raise RuntimeError("ultralytics 未安装，无法执行训练。") from exc

    model = YOLO(args.weights)
    results = model.train(
        data=str(dataset_path),
        imgsz=args.imgsz,
        epochs=args.epochs,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
    )

    RUN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "data": str(dataset_path),
        "weights": args.weights,
        "imgsz": args.imgsz,
        "epochs": args.epochs,
        "batch": args.batch,
        "device": args.device,
        "project": args.project,
        "name": args.name,
        "save_dir": str(getattr(results, "save_dir", "")),
    }
    RUN_LOG_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
