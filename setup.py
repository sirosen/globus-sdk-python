import os.path
import re

from setuptools import find_packages, setup

DEV_REQUIREMENTS = [
    # lint
    "flake8<4",
    "isort<6",
    "black==21.5b1",
    "flake8-bugbear==21.4.3",
    "mypy==0.812",
    # tests
    "pytest<7",
    "pytest-cov<3",
    "pytest-xdist<3",
    "responses==0.13.3",
    # docs
    "sphinx<5",
    "furo==2021.04.11b34",
]


def parse_version():
    # single source of truth for package version
    version_string = ""
    version_pattern = re.compile(r'__version__ = "([^"]*)"')
    with open(os.path.join("src", "globus_sdk", "version.py")) as f:
        for line in f:
            match = version_pattern.match(line)
            if match:
                version_string = match.group(1)
                break
    if not version_string:
        raise RuntimeError("Failed to parse version information")
    return version_string


def read_readme():
    with open("README.rst") as fp:
        return fp.read()


setup(
    name="globus-sdk",
    version=parse_version(),
    description="Globus SDK for Python",
    long_description=read_readme(),
    author="Globus Team",
    author_email="support@globus.org",
    url="https://github.com/globus/globus-sdk-python",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"globus_sdk": ["py.typed"]},
    python_requires=">=3.6",
    install_requires=["requests>=2.9.2,<3.0.0", "pyjwt[crypto]>=2.0.0,<3.0.0"],
    extras_require={"dev": DEV_REQUIREMENTS},
    keywords=["globus"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
