"""Bundle reviewed source, schema, docs and the existing weights for delivery."""
import hashlib
from pathlib import Path
import zipfile


def main():
    root = Path(__file__).resolve().parents[1]
    destination = root / "dist/RailwaySafety-0.2.2.zip"
    destination.parent.mkdir(exist_ok=True)
    files = []
    for directory in ("src", "apps", "assets", "docs", "notebooks", "tests"):
        files.extend(p for p in (root / directory).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    files.extend(root / name for name in (
        "README.md", "setup.py", "pyproject.toml", "MANIFEST.in", "requirements.txt",
        "requirements-dev.txt", "Dockerfile", ".dockerignore", ".gitignore", "data.json",
        "outputs/example-input.jpg", "outputs/example-result.jpg", "outputs/example-result.json",
    ) if (root / name).is_file())
    if not (root / "assets/best.pt").is_file():
        raise FileNotFoundError("assets/best.pt is required for this delivery.")
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in sorted(files):
            archive.write(source, Path("RailwaySafety") / source.relative_to(root))
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        assert archive.read("RailwaySafety/assets/best.pt") == (root / "assets/best.pt").read_bytes()
    print(destination)
    print("SHA256:", hashlib.sha256(destination.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
