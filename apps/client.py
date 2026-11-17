
import argparse
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils.inference import detect
from src.utils.inference import decode_image
from PIL import ImageDraw, ImageFont


def save_annotated_image(image, detections, destination):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=max(14, image.width // 80))
    for item in detections:
        box = item["bbox_xyxy"]
        draw.rectangle(box, outline="red", width=3)
        label = f'{item["class_name"]} {item["confidence"]:.2f}'
        position = (box[0], max(0, box[1] - font.size - 10))
        draw.rectangle(draw.textbbox(position, label, font=font), fill="red")
        draw.text(position, label, font=font, fill="white")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--device", default="cpu", help="cpu or CUDA index, e.g. 0")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--output", type=Path, help="Save detection JSON")
    parser.add_argument("--save-image", type=Path, help="Save image with detection boxes")

    args = parser.parse_args()

    image_path = Path(args.image)
    encoded = base64.b64encode(
        image_path.read_bytes()
    ).decode("ascii")

    result = detect(
        encoded,
        confidence=args.conf,
        iou=args.iou,
        device=args.device,
        image_size=args.imgsz,
    )

    payload = json.loads(result)
    formatted = json.dumps(payload, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(formatted, encoding="utf-8")
    if args.save_image:
        save_annotated_image(decode_image(encoded), payload["detections"], args.save_image)
    print(formatted)


if __name__ == "__main__":
    main()
