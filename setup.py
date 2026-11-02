from setuptools import setup, find_packages

setup(
    name="novavision-railway-safety",
    version="0.1.0",
    description="Railway defect detection component",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
)
