from pathlib import Path

from apps.audit_dataset import audit


def test_cross_split_duplicates_and_invalid_boxes(tmp_path):
    for split in ("train", "valid"):
        (tmp_path / split / "images").mkdir(parents=True)
        (tmp_path / split / "labels").mkdir()
        (tmp_path / split / "images" / "same.png").write_bytes(b"identical-image")
        (tmp_path / split / "labels" / "same.txt").write_text("0 0.5 0.5 0.2 0.2\n0 0.9 0.5 0.4 0.2\n")
    data = tmp_path / "data.yaml"
    data.write_text("train: train/images\nval: valid/images\nnames: [crack]\n")
    report = audit(data)
    assert len(report["cross_split_exact_duplicates"]) == 1
    assert len(report["issues"]) == 2
    assert report["splits"]["train"]["objects"] == {"crack": 1}
