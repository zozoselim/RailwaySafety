
from sdks.novavision.src.helper.package import PackageHelper

from ..models.PackageModel import (
    ConfigExecutor,
    RailwaySafetyExecutor,
    PackageConfigs,
    PackageModel,
    RailwayOutputs,
    PackageResponse,
    DetectionsOutput,
)


def build_response(context):
    outputs = RailwayOutputs(
        detections=DetectionsOutput(
            value=context.detections
        )
    )

    response = PackageResponse(outputs=outputs)

    configs = PackageConfigs(
        executor=ConfigExecutor(
            value=RailwaySafetyExecutor(
                value=response
            )
        )
    )

    helper = PackageHelper(
        packageModel=PackageModel,
        packageConfigs=configs,
    )

    return helper.build_model(context)
