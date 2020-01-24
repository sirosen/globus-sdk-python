import os.path
import sys

from setuptools import find_packages, setup

if sys.version_info < (3,):
    raise NotImplementedError(
        """\n
########################################
# globus-sdk does not support python 2 #
########################################"""
    )


# single source of truth for package version
version_ns = {}
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
    install_requires=["requests>=2.9.2,<3.0.0", "pyjwt[crypto]>=1.5.3,<2.0.0"],
    extras_require={
        # the development extra is for SDK developers only
        "development": [
            # testing
            "pytest<5.0",
            "pytest-cov<3.0",
            "pytest-xdist<2.0",
            # mock on py3.5 to get the same interface
            'mock==2.0.0;python_version<"3.6"',
            # mocking HTTP responses
            "httpretty==0.9.5",
        ]
    },
    include_package_data=True,
    keywords=["globus", "file transfer"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Communications :: File Sharing",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
