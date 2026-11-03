from setuptools import setup

setup(
    name="novavision-railway-safety",
    version="0.1.0",
    description="Railway defect detection component",

    install_requires=[
        "sdk",
        "ultralytics==8.4.198",
        "Pillow",
        "numpy",
        "PyYAML",
    ],

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