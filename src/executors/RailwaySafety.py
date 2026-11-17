
import os
import sys
import copy
import json

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "../../../../",
    )
)

from sdks.novavision.src.base.component import Component

if __package__:
    from ..models.PackageModel import PackageModel
    from ..utils.inference import detect_image
    from ..utils.response import build_response
else:
    from components.RailwaySafety.src.models.PackageModel import (
        PackageModel,
    )
    from components.RailwaySafety.src.utils.inference import detect_image
    from components.RailwaySafety.src.utils.response import build_response


class RailwaySafety(Component):

    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)

        self.request.model = PackageModel(**self.request.data)
        self.detections = ""

    @staticmethod
    def bootstrap(config=None):
        return {}

    def run(self):
        native_image = self.request.get_param("inputImage")
        confidence = self.request.get_param("confidence")
        iou = self.request.get_param("iou_threshold")
        device = self.request.get_param("device")
        image_size = self.request.get_param("image_size")

        settings = dict(confidence=confidence if confidence is not None else 0.25,
                        iou=iou if iou is not None else 0.45,
                        device=device if device is not None else "cpu",
                        image_size=image_size if image_size is not None else 640)
        if isinstance(native_image, list):
            if len(native_image) != 1:
                raise ValueError("RailwaySafety expects exactly one image per execution.")
            native_image = native_image[0]
        if native_image is not None:
            from sdks.novavision.src.media.image import Image as SDKImage
            from PIL import Image as PILImage
            import numpy as np

            frame = SDKImage.get_frame(img=copy.deepcopy(native_image), redis_db=self.redis_db)
            if frame is None:
                raise ValueError("NovaVision could not decode inputImage.")
            # SDK/OpenCV frames are BGR; the shared inference API takes RGB PIL.
            array = np.asarray(frame.value)
            if array.ndim != 3 or array.shape[2] != 3:
                raise ValueError("Expected a three-channel NovaVision BGR frame.")
            self.detections = detect_image(PILImage.fromarray(array[:, :, ::-1].astype(np.uint8)), **settings)
        else:
            raise ValueError("Connect Image Load or Video Feed to inputImage.")

        self.native_detections = []
        for item in json.loads(self.detections)["detections"]:
            left, top, right, bottom = item["bbox_xyxy"]
            self.native_detections.append({
                "boundingBox": {"left": left, "top": top,
                                "width": right-left, "height": bottom-top},
                "confidence": item["confidence"], "classLabel": item["class_name"],
                "classId": item["class_id"],
            })

        return build_response(self)


if __name__ == "__main__":
    from sdks.novavision.src.helper.executor import Executor

    Executor(sys.argv[1]).run()
