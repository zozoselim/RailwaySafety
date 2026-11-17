"""Evaluate existing weights; this command never trains or overwrites them."""
import argparse
import json
import hashlib
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path, help="YOLO data.yaml")
    parser.add_argument("--model", type=Path, default=Path(__file__).resolve().parents[1] / "assets/best.pt")
    parser.add_argument("--split", choices=["val", "test"], default="test")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output", type=Path, default=Path("outputs/validation.json"))
    args = parser.parse_args()
    if not args.model.is_file() or not args.data.is_file():
        parser.error("Both the model file and dataset YAML must exist.")
    from ultralytics import YOLO
    import ultralytics
    import torch

    model = YOLO(str(args.model))
    metrics = model.val(data=str(args.data.resolve()), split=args.split,
                        device=args.device, imgsz=640, workers=0,
                        project="outputs/validation", name=args.split)
    payload = {
        "split": args.split,
        "ultralytics_version": ultralytics.__version__,
        "torch_version": torch.__version__,
        "device": args.device,
        "model_sha256": hashlib.sha256(args.model.read_bytes()).hexdigest(),
        "metrics": metrics.results_dict,
        "evaluated_class_ids": metrics.box.ap_class_index.tolist(),
        "per_class_map50_95": {
            str(int(i)): {"name": model.names[int(i)],
                          "precision": float(metrics.box.p[index]),
                          "recall": float(metrics.box.r[index]),
                          "map50": float(metrics.box.ap50[index]),
                          "map50_95": float(metrics.box.maps[int(i)])}
            for index, i in enumerate(metrics.box.ap_class_index)
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, default=float), encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
