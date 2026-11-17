"""Read-only YOLO label and exact cross-split image duplication audit."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

import yaml


def audit(data_file):
    data_file = Path(data_file).resolve()
    data = yaml.safe_load(data_file.read_text(encoding="utf-8"))
    root = Path(data.get("path", "."))
    if not root.is_absolute():
        root = data_file.parent / root
    names = data["names"]
    names = dict(enumerate(names)) if isinstance(names, list) else {int(k): v for k, v in names.items()}
    report = {"names": names, "splits": {}, "issues": [], "cross_split_exact_duplicates": []}
    seen = defaultdict(list)
    for split in ("train", "val", "test"):
        if not data.get(split):
            continue
        folder = Path(data[split])
        folder = folder if folder.is_absolute() else root / folder
        if not folder.is_dir():
            raise ValueError(f"Expected an image directory for {split}: {folder}")
        counts = Counter()
        images = sorted(p for p in folder.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"})
        missing, empty = 0, 0
        for image in images:
            seen[hashlib.sha256(image.read_bytes()).hexdigest()].append((split, str(image.relative_to(root))))
            relative = image.relative_to(folder)
            label = folder.parent / "labels" / relative.with_suffix(".txt")
            if not label.is_file():
                missing += 1
                continue
            lines = label.read_text(encoding="utf-8").splitlines()
            if not any(line.strip() for line in lines):
                empty += 1
            for line_number, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                try:
                    parts = line.split()
                    if len(parts) != 5:
                        raise ValueError("expected class x y width height")
                    class_id = int(parts[0])
                    x, y, w, h = map(float, parts[1:])
                    if class_id not in names or not all(math.isfinite(v) and 0 <= v <= 1 for v in (x, y, w, h)) or w <= 0 or h <= 0:
                        raise ValueError("invalid class or normalized coordinates")
                    if min(x-w/2, y-h/2) < -1e-5 or max(x+w/2, y+h/2) > 1.00001:
                        raise ValueError("box extends beyond image")
                    counts[names[class_id]] += 1
                except ValueError as exc:
                    report["issues"].append({"label": str(label.relative_to(root)), "line": line_number, "error": str(exc)})
        report["splits"][split] = {
            "images": len(images), "missing_labels": missing, "empty_labels": empty,
            "objects": {name: counts[name] for name in names.values()},
        }
    report["cross_split_exact_duplicates"] = [items for items in seen.values() if len({s for s, _ in items}) > 1]
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path)
    parser.add_argument("--output", type=Path, default=Path("outputs/dataset-audit.json"))
    args = parser.parse_args()
    report = audit(args.data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"splits": report["splits"], "invalid_labels": len(report["issues"]),
                      "cross_split_duplicate_groups": len(report["cross_split_exact_duplicates"]),
                      "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
