from setuptools import setup

setup(
    name="novavision-railway-safety",
    version="0.2.2",
    description="Railway defect detection component",

    install_requires=[
        "ultralytics==8.4.198",
        "Pillow>=10.1",
        "numpy",
        "PyYAML",
    ],

    packages=[
        "novavision.package",
        "novavision.package.executors",
        "novavision.package.models",
        "novavision.package.utils",
        "novavision.package.assets",
    ],

    package_dir={"novavision.package": "src", "novavision.package.assets": "assets"},
    package_data={"novavision.package.assets": ["*.pt", "*.json"]},
    include_package_data=True,
    python_requires=">=3.10",
)
