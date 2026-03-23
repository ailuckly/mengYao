import argparse
import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = PROJECT_ROOT / "model" / "configs" / "final_dataset_v1.yaml"
DEFAULT_WEIGHTS = "yolo11s.pt"
RUN_LOG_PATH = PROJECT_ROOT / "records" / "logs" / "training_last_run.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLOv11 for plant recognition.")
    parser.add_argument("--data", default=str(DEFAULT_DATASET), help="dataset yaml path")
    parser.add_argument("--weights", default=DEFAULT_WEIGHTS, help="base model weights")
    parser.add_argument("--imgsz", type=int, default=640, help="image size")
    parser.add_argument("--epochs", type=int, default=100, help="training epochs")
    parser.add_argument("--batch", type=int, default=32, help="batch size")
    parser.add_argument("--device", default="0", help="cuda device id or cpu")
    parser.add_argument("--project", default="model/exports/train_runs", help="training output dir")
    parser.add_argument("--name", default="plant_yolo11_formal", help="run name")
    parser.add_argument("--optimizer", default="auto", help="optimizer name")
    parser.add_argument("--patience", type=int, default=30, help="early stopping patience")
    parser.add_argument("--workers", type=int, default=4, help="dataloader workers")
    parser.add_argument("--save-period", type=int, default=10, help="checkpoint save interval")
    parser.add_argument("--close-mosaic", type=int, default=10, help="disable mosaic in final epochs")
    parser.add_argument("--seed", type=int, default=42, help="training seed")
    parser.add_argument(
        "--cache",
        choices=["false", "ram", "disk"],
        default="false",
        help="dataset cache mode",
    )
    parser.add_argument("--cos-lr", action="store_true", help="enable cosine lr schedule")
    parser.add_argument("--resume", action="store_true", help="resume from checkpoint")
    parser.add_argument("--resume-path", default="", help="checkpoint path for resume")
    return parser.parse_args()


def resolve_project_path(project: str) -> Path:
    raw_path = Path(project).expanduser()
    if raw_path.is_absolute():
        return raw_path.resolve()
    return (PROJECT_ROOT / raw_path).resolve()


def build_summary(args: argparse.Namespace, dataset_path: Path, project_path: Path) -> dict:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "data": str(dataset_path),
        "weights": args.weights,
        "imgsz": args.imgsz,
        "epochs": args.epochs,
        "batch": args.batch,
        "device": args.device,
        "project": str(project_path),
        "name": args.name,
        "optimizer": args.optimizer,
        "patience": args.patience,
        "workers": args.workers,
        "save_period": args.save_period,
        "close_mosaic": args.close_mosaic,
        "seed": args.seed,
        "cache": args.cache,
        "cos_lr": args.cos_lr,
        "resume": args.resume,
        "resume_path": args.resume_path,
    }


def print_summary(summary: dict) -> None:
    print("=" * 72)
    print("YOLOv11 Training Configuration")
    print("=" * 72)
    for key, value in summary.items():
        print(f"{key:>14}: {value}")
    print("=" * 72)


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.data).resolve()
    project_path = resolve_project_path(args.project)
    project_path.mkdir(parents=True, exist_ok=True)

    if not dataset_path.exists():
        raise FileNotFoundError(f"dataset yaml not found: {dataset_path}")

    try:
        from ultralytics import YOLO
    except Exception as exc:
        raise RuntimeError("ultralytics 未安装，无法执行训练。") from exc

    summary = build_summary(args, dataset_path, project_path)
    print_summary(summary)

    if args.resume:
        checkpoint = Path(args.resume_path).resolve() if args.resume_path else None
        if checkpoint is None:
            raise ValueError("启用 resume 时必须提供 --resume-path。")
        if not checkpoint.exists():
            raise FileNotFoundError(f"resume checkpoint not found: {checkpoint}")

        print(f"Resuming training from: {checkpoint}")
        model = YOLO(str(checkpoint))
        results = model.train(resume=True)
    else:
        cache_mode = False if args.cache == "false" else args.cache
        print("Starting formal training run...")
        model = YOLO(args.weights)
        results = model.train(
            data=str(dataset_path),
            imgsz=args.imgsz,
            epochs=args.epochs,
            batch=args.batch,
            device=args.device,
            project=str(project_path),
            name=args.name,
            optimizer=args.optimizer,
            patience=args.patience,
            workers=args.workers,
            save_period=args.save_period,
            close_mosaic=args.close_mosaic,
            seed=args.seed,
            cache=cache_mode,
            cos_lr=args.cos_lr,
        )

    save_dir = Path(str(getattr(results, "save_dir", "")))
    summary["save_dir"] = str(save_dir)
    summary["best_checkpoint"] = str(save_dir / "weights" / "best.pt") if save_dir else ""
    summary["last_checkpoint"] = str(save_dir / "weights" / "last.pt") if save_dir else ""

    RUN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    RUN_LOG_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\nTraining finished.")
    print(f"save_dir: {summary['save_dir']}")
    print(f"best.pt : {summary['best_checkpoint']}")
    print(f"last.pt : {summary['last_checkpoint']}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
