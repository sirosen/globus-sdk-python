from distutils.core import setup

setup(name="globus-sdk-python",
      version="0.1",
      description="Globus SDK for Python",
      long_description=open("README.md").read(),
      author="Bryce Allen",
      author_email="ballen@globus.org",
      url="https://github.com/globusonline/globus-sdk-python",
      packages=["globus_sdk"],
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
