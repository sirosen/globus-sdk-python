import sys
import os.path
from setuptools import setup

tests_require = ['nose2']
# include mock (for python2)
if sys.version_info < (3, 3):
    tests_require.append('mock')

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
      packages=['globus_sdk', 'globus_sdk.transfer'],
      install_requires=[
          'requests>=2.0.0,<3.0.0',
          'six==1.10.0'
      ],
      include_package_data=True,

      # run tests with nose2
      tests_require=tests_require,
      test_suite='nose2.collector.collector',

      keywords=["globus", "file transfer"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Topic :: Communications :: File Sharing",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      )
