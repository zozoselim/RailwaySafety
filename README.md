# Railway Safety - NovaVision Package

Railway track visual inspection with YOLO11n.

## Detection classes

- rail_crack
- fastener_defect
- broken_sleeper
- obstacle

The current model does not directly measure physical
fastener looseness. Results are research/prototype outputs
and must not be used as a sole railway safety decision.

## Model

Copy the trained `best.pt` into `assets/best.pt`.

## Local inference

Install dependencies and run:

    python apps/client.py path/to/image.jpg

The result is a JSON string containing detections,
class IDs, confidence values and bounding boxes.

## NovaVision integration

SDK component interface follows the reference
EnvironmentSecretsStore package architecture.

Before production registration, validate:
- image input field and transport type
- SDK schema and PackageHelper serialization
- dependency availability inside the target container
- CPU/CUDA execution
- client compatibility
- clean installation in Dev and Prod

## Model benchmark (baseline)

Validation mAP50: 0.806
Test mAP50: 0.835
Test mAP50-95: 0.433
Test precision: 0.781
Test recall: 0.774

The benchmark is preliminary and has limited
broken-sleeper examples.
