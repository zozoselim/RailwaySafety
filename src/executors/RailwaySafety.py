
import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "../../../../",
    )
)

from sdks.novavision.src.base.component import Component

if __package__:
    from ..models.PackageModel import PackageModel
    from ..utils.inference import detect
    from ..utils.response import build_response
else:
    from components.RailwaySafety.src.models.PackageModel import (
        PackageModel,
    )
    from components.RailwaySafety.src.utils.inference import detect
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
        image = self.request.get_param("image")
        confidence = self.request.get_param("confidence")
        iou = self.request.get_param("iou_threshold")

        self.detections = detect(
            image_base64=image,
            confidence=confidence,
            iou=iou,
        )

        return build_response(self)


if __name__ == "__main__":
    from sdks.novavision.src.helper.executor import Executor

    Executor(sys.argv[1]).run()
