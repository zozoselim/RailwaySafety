
import pytest
import base64
import io
import json
from types import SimpleNamespace
from unittest.mock import Mock
from PIL import Image

from src.utils.inference import detect
from src.utils import inference


def test_invalid_confidence():
    with pytest.raises(ValueError, match="Confidence"):
        detect(encoded_image(), confidence=1.5)


def test_invalid_iou():
    with pytest.raises(ValueError, match="IoU"):
        detect(encoded_image(), iou=-0.1)


def test_invalid_image():
    with pytest.raises(ValueError):
        detect("not_valid_base64***")


def encoded_image():
    buffer = io.BytesIO()
    Image.new("RGB", (48, 32), (255, 0, 0)).save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def test_model_labels_rgb_and_settings(monkeypatch):
    box = SimpleNamespace(cls=Mock(item=lambda: 0), conf=Mock(item=lambda: .87654321),
                          xyxy=[Mock(tolist=lambda: [1, 2, 20, 25])])
    model = Mock()
    model.predict.return_value = [SimpleNamespace(boxes=[box], names={0: "checkpoint_label"})]
    monkeypatch.setattr(inference, "get_model", lambda: model)
    payload = json.loads(detect(encoded_image(), .4, .5, "cpu", 320))
    assert payload["detections"][0] == {
        "class_id": 0, "class_name": "checkpoint_label", "confidence": .876543,
        "bbox_xyxy": [1, 2, 20, 25],
    }
    assert (payload["image_width"], payload["image_height"]) == (48, 32)
    kwargs = model.predict.call_args.kwargs
    assert kwargs["source"].getpixel((0, 0)) == (255, 0, 0)
    assert kwargs["conf"] == .4 and kwargs["iou"] == .5 and kwargs["imgsz"] == 320


def test_no_detections(monkeypatch):
    model = Mock()
    model.predict.return_value = [SimpleNamespace(boxes=[], names={})]
    monkeypatch.setattr(inference, "get_model", lambda: model)
    payload = json.loads(detect(encoded_image()))
    assert payload["count"] == 0 and payload["defect_detected"] is False
    assert "safe" not in payload


def test_image_data_url():
    assert inference.decode_image("data:image/png;base64," + encoded_image()).size == (48, 32)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -.1, 1.1])
def test_nonfinite_or_out_of_range_thresholds(value):
    with pytest.raises(ValueError, match="Confidence"):
        detect(encoded_image(), confidence=value)
    with pytest.raises(ValueError, match="IoU"):
        detect(encoded_image(), iou=value)


def test_dimensions_checked_before_decode(monkeypatch):
    monkeypatch.setattr(inference, "MAX_IMAGE_PIXELS", 100)
    with pytest.raises(ValueError, match="dimensions"):
        inference.decode_image(encoded_image())


def test_missing_model_does_not_download(monkeypatch, tmp_path):
    monkeypatch.setenv("RAILWAY_SAFETY_MODEL_PATH", str(tmp_path / "missing.pt"))
    monkeypatch.setattr(inference, "_model", None)
    with pytest.raises(FileNotFoundError):
        inference.get_model()
