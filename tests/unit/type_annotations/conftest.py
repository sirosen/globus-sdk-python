import os
import re

import pytest

# mypy's only python-callable API
# see:
# https://mypy.readthedocs.io/en/stable/extending_mypy.html#integrating-mypy-into-another-python-application
from mypy import api as mypy_api


@pytest.fixture
def _in_tmp_path(tmp_path):
    cur = os.getcwd()
    try:
        os.chdir(tmp_path)
        yield
    finally:
        os.chdir(cur)


@pytest.fixture
def run_reveal_type(tmp_path, _in_tmp_path):
    content_path = tmp_path / "reveal_type_test.py"

    def func(code_snippet, *, preamble="import globus_sdk\n\n"):
        content_path.write_text(preamble + f"reveal_type({code_snippet})")
        # note: these invocations are slow, but no significant speed improvement was
        # offered by running dmypy for this use-case
        result = mypy_api.run(["reveal_type_test.py"])
        stdout = result[0]
        print(result)
        # mypy reveal_type shows notes like
        #   note: Revealed type is "Union[builtins.str, None]"
        # find and extract with a regex
        match = re.search(r'note: Revealed type is "([^"]+)"', stdout)
        assert match is not None
        return match.group(1)

    return func
