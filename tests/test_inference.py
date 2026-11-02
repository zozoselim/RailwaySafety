
import pytest

from src.utils.inference import detect


def test_invalid_confidence():
    with pytest.raises(ValueError):
        detect("", confidence=1.5)


def test_invalid_iou():
    with pytest.raises(ValueError):
        detect("", iou=-0.1)


def test_invalid_image():
    with pytest.raises(ValueError):
        detect("not_valid_base64***")
