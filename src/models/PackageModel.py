
from typing import Literal, Union
from pydantic import Field

from sdks.novavision.src.base.model import (
    Config,
    Configs,
    Inputs,
    Output,
    Outputs,
    Package,
    Request,
    Response,
)


class ImageInput(Config):
    name: Literal["image"] = "image"
    value: str = ""
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Input Image (Base64)"
        json_schema_extra = {
            "shortDescription": "Base64 encoded railway image."
        }


class RailwayInputs(Inputs):
    image: ImageInput


class Confidence(Config):
    name: Literal["confidence"] = "confidence"
    value: float = Field(default=0.25, ge=0, le=1)
    type: Literal["number"] = "number"
    field: Literal["numberInput"] = "numberInput"

    class Config:
        title = "Confidence Threshold"


class IoUThreshold(Config):
    name: Literal["iou_threshold"] = "iou_threshold"
    value: float = Field(default=0.45, ge=0, le=1)
    type: Literal["number"] = "number"
    field: Literal["numberInput"] = "numberInput"

    class Config:
        title = "IoU Threshold"


class RailwayConfigs(Configs):
    confidence: Confidence
    iou_threshold: IoUThreshold


class DetectionsOutput(Output):
    name: Literal["detections"] = "detections"
    value: str
    type: Literal["string"] = "string"

    class Config:
        title = "Railway Defect Detections"


class RailwayOutputs(Outputs):
    detections: DetectionsOutput


class PackageRequest(Request):
    inputs: RailwayInputs
    configs: RailwayConfigs

    class Config:
        json_schema_extra = {"target": "configs"}


class PackageResponse(Response):
    outputs: RailwayOutputs


class RailwaySafetyExecutor(Config):
    name: Literal["RailwaySafety"] = "RailwaySafety"
    value: Union[PackageRequest, PackageResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "Railway Safety"
        json_schema_extra = {"target": {"value": 0}}


class ConfigExecutor(Config):
    name: Literal["ConfigExecutor"] = "ConfigExecutor"
    value: RailwaySafetyExecutor
    type: Literal["executor"] = "executor"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Task"
        json_schema_extra = {"target": "value"}


class PackageConfigs(Configs):
    executor: ConfigExecutor


class PackageModel(Package):
    configs: PackageConfigs
    type: Literal["component"] = "component"
    name: Literal["RailwaySafety"] = "RailwaySafety"
