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

import pytest

try:
    import sysconfig
except ImportError:
    sysconfig = None

try:
    from PyInstaller import __main__ as pyi_main
except ImportError:
    pyi_main = None


def shared_libraries_are_available():
    """
    check if python was built with --enable-shared or if the system python (with
    dynamically linked libs) is in use
    default to guessing that the shared libs are not available (be conservative)
    """
    # if detection isn't possible because sysconfig isn't available (py2) then fail
    if not sysconfig:
        return False
    enable_shared = sysconfig.get_config_var("Py_ENABLE_SHARED")
    return enable_shared == 1


@pytest.mark.skipif(
    not shared_libraries_are_available(),
    reason="requires that python was built with --enable-shared",
)
@pytest.mark.skipif(
    not pyi_main, reason="pyinstaller not available in test environment"
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
