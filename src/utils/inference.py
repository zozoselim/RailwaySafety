"""Inference shared by the local client and the NovaVision executor."""

import base64
import binascii
import io
import json
import math
import os
from pathlib import Path
from threading import RLock

from PIL import Image, ImageOps, UnidentifiedImageError


MAX_IMAGE_BYTES = 25 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
_package_assets = Path(__file__).resolve().parents[1] / "assets"
MODEL_PATH = (_package_assets if _package_assets.is_dir() else
              Path(__file__).resolve().parents[2] / "assets") / "best.pt"
_model = None
_model_path = None
_lock = RLock()


def get_model():
    """Load local weights once. Never substitute/download generic YOLO weights."""
    global _model, _model_path
    path = Path(os.environ.get("RAILWAY_SAFETY_MODEL_PATH", MODEL_PATH)).resolve()
    with _lock:
        if _model is None or _model_path != path:
            if not path.is_file():
                raise FileNotFoundError(f"Model not found: {path}")
            from ultralytics import YOLO

            model = YOLO(str(path))
            if model.task != "detect":
                raise ValueError("RailwaySafety requires a YOLO detection model.")
            _model = model
            _model_path = path
        return _model


def decode_image(encoded_image):
    if not isinstance(encoded_image, str):
        raise ValueError("Image must be a Base64 string.")
    encoded = encoded_image
    if encoded.startswith("data:"):
        header, separator, encoded = encoded.partition(",")
        if not separator or not header.startswith("data:image/") or not header.endswith(";base64"):
            raise ValueError("Expected an image Base64 data URL.")
    if len(encoded) > 4 * ((MAX_IMAGE_BYTES + 2) // 3):
        raise ValueError("Image exceeds 25 MiB.")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Invalid Base64 image.") from exc
    if not raw or len(raw) > MAX_IMAGE_BYTES:
        raise ValueError("Invalid image size.")
    try:
        with Image.open(io.BytesIO(raw)) as image:
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ValueError("Image dimensions too large.")
            return ImageOps.exif_transpose(image).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("Unsupported or oversized image data.") from exc


def detect(image_base64, confidence=0.25, iou=0.45, device="cpu", image_size=640):
    return detect_image(decode_image(image_base64), confidence, iou, device, image_size)


def detect_image(image, confidence=0.25, iou=0.45, device="cpu", image_size=640):
    """Run on a decoded RGB PIL image, including frames supplied by the SDK."""
    confidence, iou = float(confidence), float(iou)
    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError("Confidence must be between 0 and 1.")
    if not math.isfinite(iou) or not 0 <= iou <= 1:
        raise ValueError("IoU must be between 0 and 1.")
    if isinstance(image_size, bool) or int(image_size) != float(image_size) or not 32 <= int(image_size) <= 4096:
        raise ValueError("Image size must be an integer between 32 and 4096.")
    if not isinstance(image, Image.Image) or image.width * image.height > MAX_IMAGE_PIXELS:
        raise ValueError("Expected a PIL image of at most 25 million pixels.")
    image = image.convert("RGB")
    with _lock:
        model = get_model()
        # PIL has RGB semantics. YOLO interprets NumPy input as BGR.
        results = model.predict(source=image, conf=confidence, iou=iou,
                                device=device, imgsz=int(image_size), verbose=False)
        detections = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                class_id = int(box.cls.item())
                detections.append({
                    "class_id": class_id,
                    "class_name": result.names[class_id],
                    "confidence": round(float(box.conf.item()), 6),
                    "bbox_xyxy": [round(float(v), 2) for v in box.xyxy[0].tolist()],
                })
    return json.dumps({
        "detections": detections,
        "count": len(detections),
        "image_width": image.width,
        "image_height": image.height,
        "coordinate_format": "xyxy_pixels",
        "defect_detected": bool(detections),
    }, allow_nan=False)
