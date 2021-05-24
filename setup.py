import os.path

from setuptools import find_packages, setup

# single source of truth for package version
version_ns = {}  # type: ignore
with open(os.path.join("globus_sdk", "version.py")) as f:
    exec(f.read(), version_ns)

setup(
    name="globus-sdk",
    version=version_ns["__version__"],
    description="Globus SDK for Python",
    long_description=open("README.rst").read(),
    author="Globus Team",
    author_email="support@globus.org",
    url="https://github.com/globus/globus-sdk-python",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.6",
    install_requires=["requests>=2.9.2,<3.0.0", "pyjwt[crypto]>=2.0.0,<3.0.0"],
    extras_require={
        # the dev extra is for SDK developers only
        "dev": [
            # drive testing with tox
            "tox<4",
            # linting
            "flake8<4",
            "isort<6",
            "black==21.5b1",
            "flake8-bugbear==21.4.3",
            "mypy==0.812",
            # testing
            "pytest<7",
            "pytest-cov<3",
            "pytest-xdist<3",
            # mocking HTTP responses
            "responses==0.13.3",
            # builds + uploads to pypi
            "twine<4",
            "wheel==0.36.2",
            # docs
            "sphinx<5",
            "sphinx-material==0.0.32",
        ]
    },
    include_package_data=True,
    keywords=["globus", "file transfer"],
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
