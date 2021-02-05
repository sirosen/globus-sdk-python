#
# This module is based on the PyInstaller Hook Sample test
# see:  https://github.com/pyinstaller/hooksample
#
# this is a pytest test which
# - runs pyinstaller on the SDK with a simple app
# - runs the app
#
# the app imports the SDK and constructs a client object to make
# sure that imports are working correctly
# because client object creation loads config, it also ensures that config data can be
# read

import subprocess
import sysconfig

import pytest
from PyInstaller import __main__ as pyi_main


def shared_libraries_are_available():
    """
    check if python was built with --enable-shared or if the system python (with
    dynamically linked libs) is in use
    default to guessing that the shared libs are not available (be conservative)
    """
    enable_shared = sysconfig.get_config_var("Py_ENABLE_SHARED")
    return enable_shared == 1


@pytest.mark.skipif(
    not shared_libraries_are_available(),
    reason="requires that python was built with --enable-shared",
)
def test_pyinstaller_hook(tmp_path):
    appfile = tmp_path / "sample.py"
    appfile.write_text(
        """\
import globus_sdk
ac = globus_sdk.AuthClient()
"""
    )
    pyi_main.run(
        [
            "--workpath",
            str(tmp_path / "build"),
            "--distpath",
            str(tmp_path / "dist"),
            "--specpath",
            str(tmp_path),
            str(appfile),
        ]
    )
    subprocess.run([str(tmp_path / "dist" / "sample" / "sample")], check=True)
