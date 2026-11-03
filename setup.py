from setuptools import setup

setup(
    name="novavision-railway-safety",
    version="0.1.0",
    description="Railway defect detection component",
    packages=[
        "novavision.package",
        "novavision.package.executors",
        "novavision.package.models",
        "novavision.package.utils",
    ],
    package_dir={"novavision.package": "src"},
    include_package_data=True,
    python_requires=">=3.10",
)