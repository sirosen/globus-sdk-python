import os
import shutil
import tempfile

import pytest

import globus_sdk

try:
    import mock
except ImportError:
    from unittest import mock


_IS_WINDOWS = os.name == "nt"


@pytest.fixture(autouse=True)
def mocked_homedir():
    tempdir = tempfile.mkdtemp()

    def mock_expanduser(path):
        return os.path.join(tempdir, path.replace("~/", ""))

    try:
        if _IS_WINDOWS:
            os.mkdir(os.path.join(tempdir, "Globus Connect"))
            with mock.patch.dict(os.environ):
                os.environ["LOCALAPPDATA"] = tempdir
                yield tempdir
        else:
            os.makedirs(os.path.join(tempdir, ".globusonline/lta"))
            with mock.patch("os.path.expanduser", mock_expanduser):
                yield tempdir

    finally:
        shutil.rmtree(tempdir)


@pytest.fixture
def write_gcp_id_file(mocked_homedir):
    def _func_fixture(epid):
        if _IS_WINDOWS:
            fpath = os.path.join(mocked_homedir, "Globus Connect", "client-id.txt")
        else:
            fpath = os.path.join(mocked_homedir, ".globusonline/lta/client-id.txt")
        with open(fpath, "w") as f:
            f.write(epid)
            f.write("\n")

    return _func_fixture


@pytest.fixture
def local_gcp():
    return globus_sdk.LocalGlobusConnectPersonal()


@pytest.mark.skipif(not _IS_WINDOWS, reason="test requires Windows")
def test_localep_localappdata_notset(local_gcp):
    with mock.patch.dict(os.environ):
        del os.environ["LOCALAPPDATA"]
        with pytest.raises(globus_sdk.GlobusSDKUsageError):
            local_gcp.endpoint_id


def test_localep_load_id(local_gcp, write_gcp_id_file):
    assert local_gcp.endpoint_id is None
    write_gcp_id_file("foobar")
    assert local_gcp.endpoint_id == "foobar"
    write_gcp_id_file("xyz")
    assert local_gcp.endpoint_id == "foobar"
    del local_gcp.endpoint_id
    assert local_gcp.endpoint_id == "xyz"
