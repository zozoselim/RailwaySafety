"""Inspect a trusted local checkpoint in an environment with working PyTorch."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path, nargs="?", default=Path(__file__).resolve().parents[1] / "assets/best.pt")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.model.is_file():
        parser.error(f"Model not found: {args.model}")
    from ultralytics import YOLO

    model = YOLO(str(args.model))
    payload = {
        "sha256": hashlib.sha256(args.model.read_bytes()).hexdigest(),
        "task": model.task,
        "names": model.names,
        "ultralytics_version": model.ckpt.get("version"),
        "training_metrics": model.ckpt.get("train_metrics"),
        "training_arguments": model.ckpt.get("train_args"),
    }
    report = json.dumps(payload, indent=2, default=str)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
