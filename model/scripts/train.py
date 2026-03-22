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
    parser.add_argument("--resume", action="store_true", help="resume from checkpoint")
    parser.add_argument("--resume-path", default="", help="checkpoint path for resume")
    return parser.parse_args()


def resolve_project_path(project: str) -> Path:
    raw_path = Path(project).expanduser()
    if raw_path.is_absolute():
        return raw_path.resolve()
    return (PROJECT_ROOT / raw_path).resolve()


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.data).resolve()
    project_path = resolve_project_path(args.project)
    if not dataset_path.exists():
        raise FileNotFoundError(f"dataset yaml not found: {dataset_path}")

    try:
        from ultralytics import YOLO
    except Exception as exc:
        raise RuntimeError("ultralytics 未安装，无法执行训练。") from exc

    if args.resume:
        checkpoint = Path(args.resume_path).resolve() if args.resume_path else None
        if checkpoint is None:
            raise ValueError("启用 resume 时必须提供 --resume-path。")
        if not checkpoint.exists():
            raise FileNotFoundError(f"resume checkpoint not found: {checkpoint}")

        model = YOLO(str(checkpoint))
        results = model.train(resume=True)
    else:
        model = YOLO(args.weights)
        results = model.train(
            data=str(dataset_path),
            imgsz=args.imgsz,
            epochs=args.epochs,
            batch=args.batch,
            device=args.device,
            project=str(project_path),
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
        "project": str(project_path),
        "name": args.name,
        "resume": args.resume,
        "resume_path": args.resume_path,
        "save_dir": str(getattr(results, "save_dir", "")),
    }
    RUN_LOG_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
