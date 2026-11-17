
from typing import List, Literal, Union
from pydantic import Field, validator

from sdks.novavision.src.base.model import (
    Config,
    Configs,
    Input,
    Inputs,
    Output,
    Outputs,
    Package,
    Request,
    Response,
    Image,
    Detection,
)


class NativeImageInput(Input):
    name: Literal["inputImage"] = "inputImage"
    value: Union[List[Image], Image]
    type: str = "object"

    @validator("type", pre=True, always=True)
    def set_type_based_on_value(cls, value, values):
        return "list" if isinstance(values.get("value"), list) else "object"

    class Config:
        title = "Image (Image Load / Video Feed)"


class RailwayInputs(Inputs):
    # Direct required reference, matching the platform's drawing components.
    # Optional/null wrappers can hide the connector in the Flow editor.
    inputImage: NativeImageInput


class Confidence(Config):
    name: Literal["confidence"] = "confidence"
    value: float = Field(default=0.25, ge=0, le=1)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Confidence Threshold"


class IoUThreshold(Config):
    name: Literal["iou_threshold"] = "iou_threshold"
    value: float = Field(default=0.45, ge=0, le=1)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "IoU Threshold"


class Device(Config):
    name: Literal["device"] = "device"
    value: str = "cpu"
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Inference Device (cpu or CUDA index)"


class ImageSize(Config):
    name: Literal["image_size"] = "image_size"
    value: int = Field(default=640, ge=32, le=4096)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Inference Image Size"


class RailwayConfigs(Configs):
    confidence: Confidence = Field(default_factory=Confidence)
    iou_threshold: IoUThreshold = Field(default_factory=IoUThreshold)
    device: Device = Field(default_factory=Device)
    image_size: ImageSize = Field(default_factory=ImageSize)


class DetectionsOutput(Output):
    name: Literal["detections"] = "detections"
    value: str
    type: Literal["string"] = "string"

    class Config:
        title = "Railway Defect Detections"


class NativeDetectionsOutput(Output):
    name: Literal["outputDetections"] = "outputDetections"
    value: List[Detection]
    type: Literal["list"] = "list"

    class Config:
        title = "Detections (Draw Bounding Box / Draw Label)"


class RailwayOutputs(Outputs):
    detections: DetectionsOutput
    outputDetections: NativeDetectionsOutput


class PackageRequest(Request):
    inputs: RailwayInputs
    configs: RailwayConfigs = Field(default_factory=RailwayConfigs)

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
