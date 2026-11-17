"""Run with the real NovaVision SDK and PyTorch; no Suite connection required."""
import base64
import io
import json
import os
from pathlib import Path
import sys

os.environ.setdefault("NAME", "novavision/railway-safety-smoke")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from PIL import Image
from sdks.novavision.src.base.request import Request
from src.executors.RailwaySafety import RailwaySafety
from src.models.PackageModel import (
    PackageModel, PackageConfigs, ConfigExecutor, RailwaySafetyExecutor,
    PackageRequest, RailwayInputs, ImageInput, NativeImageInput,
)
from sdks.novavision.src.base.model import Image as SDKImage


def run(inputs, size):
    package = PackageModel(uID="railway-smoke", configs=PackageConfigs(
        executor=ConfigExecutor(value=RailwaySafetyExecutor(value=PackageRequest(inputs=inputs)))))
    request = Request(package.model_dump() if hasattr(package, "model_dump") else package.dict())
    context = RailwaySafety(request, RailwaySafety.bootstrap())
    response = context.run()
    data = response.model_dump() if hasattr(response, "model_dump") else response.dict()
    payload = data["configs"]["executor"]["value"]["value"]["outputs"]
    result = json.loads(payload["detections"]["value"])
    assert (result["image_width"], result["image_height"]) == size
    assert isinstance(payload["outputDetections"]["value"], list)
    assert len(payload["outputDetections"]["value"]) == result["count"]
    for native, item in zip(payload["outputDetections"]["value"], result["detections"]):
        left, top, right, bottom = item["bbox_xyxy"]
        assert native["classLabel"] == item["class_name"]
        assert native["classId"] == item["class_id"]
        assert native["boundingBox"] == {"left": left, "top": top, "width": right-left, "height": bottom-top}
    return result


def main():
    image = Image.open(sys.argv[1]).convert("RGB") if len(sys.argv) > 1 else Image.new("RGB", (64, 48), (255, 0, 0))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    first = run(RailwayInputs(image=ImageInput(value=base64.b64encode(buffer.getvalue()).decode())), image.size)
    bgr = np.asarray(image)[:, :, ::-1].copy()
    native = SDKImage(name="frame", uID="frame-smoke", mimeType="image/png", type="image",
                      encoding="bytes", value=base64.b64encode(bgr.tobytes()).decode(),
                      shape_key=base64.b64encode(np.array(bgr.shape, dtype=np.int64).tobytes()).decode())
    second = run(RailwayInputs(inputImage=NativeImageInput(value=native)), image.size)
    assert first == second, "Base64 and native BGR input must agree"
    print("Real SDK + real model: Base64 and native bytes input, defaults and both outputs passed.")


if __name__ == "__main__":
    main()
