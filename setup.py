import sys
from setuptools import setup

tests_require = ['nose2']
# include mock (for python2)
if sys.version_info < (3,3):
    tests_require.append('mock')

setup(name="globus-sdk",
      version="0.1",
      description="Globus SDK for Python",
      long_description=open("README.md").read(),
      author="Bryce Allen",
      author_email="ballen@globus.org",
      url="https://github.com/globusonline/globus-sdk-python",
      packages=['globus_sdk', 'globus_sdk.transfer'],
      package_data={'': ['*.cfg']},
      install_requires=[
          'requests>=2.0.0,<3.0.0',
          'six==1.10.0'
      ],

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
          "Topic :: Communications :: File Sharing",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      )
