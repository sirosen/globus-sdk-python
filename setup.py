import os.path
import sys
import warnings

from setuptools import find_packages, setup

if sys.version_info < (2, 7):
    raise NotImplementedError(
        """\n
##############################################################
# globus-sdk does not support python versions older than 2.7 #
##############################################################"""
    )

# warn on older/untested python3s
# it's not disallowed, but it could be an issue for some people
if sys.version_info > (3,) and sys.version_info < (3, 5):
    warnings.warn(
        "Installing globus-sdk on Python 3 versions older than 3.5 "
        "may result in degraded functionality or even errors."
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
    install_requires=[
        "requests>=2.9.2,<3.0.0",
        "six>=1.10.0,<2.0.0",
        "pyjwt[crypto]>=1.5.3,<2.0.0",
    ],
    extras_require={
        # empty extra included to support older installs
        "jwt": [],
        # the development extra is for SDK developers only
        "development": [
            # drive testing with tox
            "tox>=3.5.3,<4.0",
            # linting
            "flake8>=3.0,<4.0",
            'isort>=5.1.4,<6.0;python_version>="3.6"',
            # black requires py3.6+
            # refrain from using 19.10b0 or later until
            #   https://github.com/psf/black/issues/1288
            # is fixed
            'black==19.3b0;python_version>="3.6"',
            # flake-bugbear requires py3.6+
            'flake8-bugbear==20.1.4;python_version>="3.6"',
            # testing
            "pytest<5.0",
            "pytest-cov<3.0",
            "pytest-xdist<2.0",
            # mock on py2, py3.4 and py3.5
            # not just py2: py3 versions of mock don't all have the same
            # interface!
            'mock==2.0.0;python_version<"3.6"',
            # mocking HTTP responses
            "httpretty==0.9.5",
            # builds + uploads to pypi
            'twine==3.2.0;python_version>="3.6"',
            'wheel==0.34.2;python_version>="3.6"',
            # docs
            'sphinx==3.1.2;python_version>="3.6"',
            'sphinx-material==0.0.30;python_version>="3.6"',
        ],
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
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Communications :: File Sharing",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
