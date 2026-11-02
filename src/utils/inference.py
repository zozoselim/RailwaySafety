
import base64
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "assets"
    / "best.pt"
)

CLASS_NAMES = {
    0: "rail_crack",
    1: "fastener_defect",
    2: "broken_sleeper",
    3: "obstacle",
}

_model = None


def get_model():
    global _model

    if _model is None:
        if not MODEL_PATH.is_file():
            raise FileNotFoundError(
                f"Model not found: {MODEL_PATH}"
            )

        _model = YOLO(str(MODEL_PATH))

    return _model


def decode_image(encoded_image):
    if not isinstance(encoded_image, str):
        raise ValueError("Image must be a Base64 string.")

    encoded = encoded_image.split(",", 1)[-1]

    try:
        raw = base64.b64decode(
            encoded,
            validate=True,
        )
    except Exception as exc:
        raise ValueError("Invalid Base64 image.") from exc

    if not raw or len(raw) > 25 * 1024 * 1024:
        raise ValueError("Invalid image size.")

    try:
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            if image.width * image.height > 25_000_000:
                raise ValueError("Image dimensions too large.")
            return image.convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Unsupported image data.") from exc


def detect(image_base64, confidence=0.25, iou=0.45):
    confidence = float(confidence)
    iou = float(iou)

    if not (0 <= confidence <= 1):
        raise ValueError("Confidence must be between 0 and 1.")

    if not (0 <= iou <= 1):
        raise ValueError("IoU must be between 0 and 1.")

    image = decode_image(image_base64)
    frame = np.asarray(image)

    results = get_model().predict(
        source=frame,
        conf=confidence,
        iou=iou,
        verbose=False,
    )

    detections = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls.item())

            detections.append({
                "class_id": class_id,
                "class_name": CLASS_NAMES.get(
                    class_id,
                    str(class_id),
                ),
                "confidence": round(
                    float(box.conf.item()), 6
                ),
                "bbox_xyxy": [
                    round(float(v), 2)
                    for v in box.xyxy[0].tolist()
                ],
            })

    return json.dumps({
        "detections": detections,
        "count": len(detections),
        "image_width": image.width,
        "image_height": image.height,
    })
