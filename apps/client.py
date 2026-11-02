
import argparse
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils.inference import detect


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)

    args = parser.parse_args()

    image_path = Path(args.image)
    encoded = base64.b64encode(
        image_path.read_bytes()
    ).decode("ascii")

    result = detect(
        encoded,
        confidence=args.conf,
        iou=args.iou,
    )

    print(json.dumps(json.loads(result), indent=2))


if __name__ == "__main__":
    main()
