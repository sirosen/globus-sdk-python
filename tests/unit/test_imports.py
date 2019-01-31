"""
Various tests for imports from the SDK to ensure that our `__all__`
declarations are correct and complete.

To ensure that we aren't contaminating these tests with the current
interpreter's state, invoke these via subprocess check_call() calls.
These should all be using `shell=True` (the subprocess invoked interpreter
doesn't behave correctly without it).
"""
import os
import subprocess
import sys

import pytest

PYTHON_BINARY = os.environ.get("GLOBUS_TEST_PY", sys.executable)


@pytest.mark.parametrize(
    "importstring",
    [
        "from globus_sdk import *",
        "from globus_sdk import TransferClient, AuthClient, SearchClient",
    ],
)
def test_import_str(importstring):
    proc = subprocess.Popen(
        '{} -c "{}"'.format(PYTHON_BINARY, importstring),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    status = proc.wait()
    assert status == 0, str(proc.communicate())
