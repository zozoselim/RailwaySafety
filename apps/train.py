"""Optional fine-tuning; writes a new run and leaves assets/best.pt intact."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path)
    parser.add_argument("--model", type=Path, default=Path(__file__).resolve().parents[1] / "assets/best.pt")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    if not args.model.is_file() or not args.data.is_file():
        parser.error("Both the model file and dataset YAML must exist.")
    from ultralytics import YOLO

    YOLO(str(args.model)).train(data=str(args.data.resolve()), epochs=args.epochs,
                               batch=args.batch, device=args.device, imgsz=640,
                               workers=0, seed=0, project="runs/railway_training",
                               name="finetune", exist_ok=False)


if __name__ == "__main__":
    main()
