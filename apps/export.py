
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.models.PackageModel import PackageModel


if hasattr(PackageModel, "model_json_schema"):
    schema = PackageModel.model_json_schema()
else:
    schema = PackageModel.schema()

with open(ROOT / "data.json", "w", encoding="utf-8") as file:
    json.dump(
        schema,
        file,
        indent=2,
        ensure_ascii=False,
    )

print("data.json exported successfully.")
