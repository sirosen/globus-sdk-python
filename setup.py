import warnings
import os.path
import sys
from setuptools import setup, find_packages


if sys.version_info < (2, 7):
    raise NotImplementedError("""\n
##############################################################
# globus-sdk does not support python versions older than 2.7 #
##############################################################""")

# warn on older/untested python3s
# it's not disallowed, but it could be an issue for some people
if sys.version_info > (3,) and sys.version_info < (3, 4):
    warnings.warn(
        'Installing globus-sdk on Python 3 versions older than 3.4 '
        'may result in degraded functionality or even errors.')


# single source of truth for package version
version_ns = {}
with open(os.path.join("globus_sdk", "version.py")) as f:
    exec(f.read(), version_ns)

setup(name="globus-sdk",
      version=version_ns["__version__"],
      description="Globus SDK for Python",
      long_description=open("README.rst").read(),
      author="Globus Team",
      author_email="support@globus.org",
      url="https://github.com/globus/globus-sdk-python",
      packages=find_packages(exclude=['tests', 'tests.*']),
      install_requires=[
          'requests>=2.0.0,<3.0.0',
          'six>=1.10.0,<2.0.0',
          'pyjwt[crypto]>=1.5.3,<2.0.0'
      ],

      extras_require={
          # empty extra included to support older installs
          'jwt': [],

          # the _development extra is for SDK developers only
          'development': [
              # testing reqs
              'flake8>=3.0,<4.0',
              'pytest>=3.7.4,<4.0',
              'pytest-cov>=2.5.1,<3.0',
              'pytest-xdist>=1.22.5,<2.0',
              # mock on py2 only
              'mock==2.0.0;python_version<"3.0"',
              # mocking HTTP responses
              'httpretty==0.9.5',

              # uploads to pypi
              'twine==1.9.1',

              # docs
              'sphinx==1.4.1',
              'guzzle_sphinx_theme==0.7.11',
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
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Topic :: Communications :: File Sharing",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      )
