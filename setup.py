from setuptools import setup, find_packages

setup(
    name="json-to-csv",
    version="1.0.0",
    packages=find_packages(),
    package_data={"json_to_csv": ["static/**/*", "static/*"]},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "json-to-csv=json_to_csv.cli:main",
        ],
    },
)
