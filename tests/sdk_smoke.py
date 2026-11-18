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
    PackageRequest, RailwayInputs, NativeImageInput,
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
    schema = PackageModel.model_json_schema() if hasattr(PackageModel, "model_json_schema") else PackageModel.schema()
    definitions = schema.get("$defs", schema.get("definitions"))
    inputs = definitions["RailwayInputs"]
    assert inputs["required"] == ["inputImage"]
    assert "$ref" in inputs["properties"]["inputImage"]
    assert "anyOf" not in inputs["properties"]["inputImage"]
    image = Image.open(sys.argv[1]).convert("RGB") if len(sys.argv) > 1 else Image.new("RGB", (64, 48), (255, 0, 0))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    bgr = np.asarray(image)[:, :, ::-1].copy()
    shape = base64.b64encode(np.array(bgr.shape, dtype=np.int64).tobytes()).decode()
    encoded = SDKImage(name="frame", uID="frame-smoke", mimeType="image/png", type="image",
                       encoding="base64", value=base64.b64encode(buffer.getvalue()).decode(), shape_key=shape)
    first = run(RailwayInputs(inputImage=NativeImageInput(value=encoded)), image.size)
    native = SDKImage(name="frame", uID="frame-smoke", mimeType="image/png", type="image",
                      encoding="bytes", value=base64.b64encode(bgr.tobytes()).decode(),
                      shape_key=base64.b64encode(np.array(bgr.shape, dtype=np.int64).tobytes()).decode())
    second = run(RailwayInputs(inputImage=NativeImageInput(value=native)), image.size)
    listed = NativeImageInput(value=[native])
    assert listed.type == "list"
    third = run(RailwayInputs(inputImage=listed), image.size)
    assert first == second, "Base64 and native BGR input must agree"
    assert second == third, "Image Load singleton lists must preserve detections"
    print("Real SDK + real model: required input connector schema, native Base64/bytes/singleton-list inputs and both outputs passed.")


if __name__ == "__main__":
    main()
