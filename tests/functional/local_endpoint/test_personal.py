import os
import shutil
import tempfile

import pytest

import globus_sdk
from tests.common import register_api_route

_IS_WINDOWS = os.name == "nt"

BASE32_ID = "u_vy2bvggsoqi6loei3oxdvc5fiu"


def _compute_confdir(homedir):
    if _IS_WINDOWS:
        return os.path.join(homedir, "Globus Connect")
    else:
        return os.path.join(homedir, ".globusonline/lta")


@pytest.fixture(autouse=True)
def mocked_homedir(monkeypatch):
    tempdir = tempfile.mkdtemp()

    def mock_expanduser(path):
        return os.path.join(tempdir, path.replace("~/", ""))

    try:
        confdir = _compute_confdir(tempdir)
        os.makedirs(confdir)
        if _IS_WINDOWS:
            monkeypatch.setitem(os.environ, "LOCALAPPDATA", tempdir)
        else:
            monkeypatch.setattr(os.path, "expanduser", mock_expanduser)
        yield tempdir

    finally:
        shutil.rmtree(tempdir)


@pytest.fixture
def mocked_confdir(mocked_homedir):
    return _compute_confdir(mocked_homedir)


@pytest.fixture
def write_gcp_id_file(mocked_confdir):
    def _func_fixture(epid):
        fpath = os.path.join(mocked_confdir, "client-id.txt")
        with open(fpath, "w") as f:
            f.write(epid)
            f.write("\n")

    return _func_fixture


@pytest.fixture
def write_gridmap(mocked_confdir):
    def _func_fixture(data):
        fpath = os.path.join(mocked_confdir, "gridmap")
        with open(fpath, "w") as f:
            f.write(data)

    return _func_fixture


@pytest.fixture
def local_gcp():
    return globus_sdk.LocalGlobusConnectPersonal()


@pytest.fixture
def auth_client():
    return globus_sdk.AuthClient()


@pytest.mark.skipif(not _IS_WINDOWS, reason="test requires Windows")
def test_localep_localappdata_notset(local_gcp, monkeypatch):
    monkeypatch.delitem(os.environ, "LOCALAPPDATA")
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


def test_load_id_no_confdir(local_gcp, mocked_confdir):
    shutil.rmtree(mocked_confdir)
    assert local_gcp.endpoint_id is None


def test_get_owner_info(local_gcp, write_gridmap, auth_client):
    write_gridmap(
        '"/C=US/O=Globus Consortium/OU=Globus Connect User/CN=sirosen" sirosen\n'
    )
    assert local_gcp.get_owner_info() == ("sirosen@globusid.org", False)

    register_api_route(
        "auth",
        "/v2/api/identities",
        json={
            "identities": [
                {
                    "email": "sirosen@globus.org",
                    "id": "ae332d86-d274-11e5-b885-b31714a110e9",
                    "identity_provider": "41143743-f3c8-4d60-bbdb-eeecaba85bd9",
                    "identity_type": "login",
                    "name": "Stephen Rosen",
                    "organization": "Globus Team",
                    "status": "used",
                    "username": "sirosen@globusid.org",
                }
            ]
        },
    )
    data = local_gcp.get_owner_info(auth_client)
    assert isinstance(data, dict)
    assert data["id"] == "ae332d86-d274-11e5-b885-b31714a110e9"


def test_get_owner_info_b32_mode(local_gcp, write_gridmap, auth_client):
    write_gridmap(
        f'"/C=US/O=Globus Consortium/OU=Globus Connect User/CN={BASE32_ID}" sirosen\n'
    )
    assert local_gcp.get_owner_info() == ("ae341a98-d274-11e5-b888-dbae3a8ba545", True)

    register_api_route(
        "auth",
        "/v2/api/identities",
        json={
            "identities": [
                {
                    "email": "sirosen@globus.org",
                    "id": "ae341a98-d274-11e5-b888-dbae3a8ba545",
                    "identity_provider": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
                    "identity_type": "login",
                    "name": "Stephen Rosen",
                    "organization": "Globus Team",
                    "status": "used",
                    "username": "sirosen@globus.org",
                }
            ]
        },
    )
    data = local_gcp.get_owner_info(auth_client)
    assert isinstance(data, dict)
    assert data["id"] == "ae341a98-d274-11e5-b888-dbae3a8ba545"


# these things are close to the right thing, but each is somehow wrong
@pytest.mark.parametrize(
    "cn",
    [
        # no 'u_'
        BASE32_ID[2:],
        # short one char
        BASE32_ID[:-1],
        # invalid b32 char included
        BASE32_ID[:-1] + "/",
    ],
)
def test_get_owner_info_b32_mode_invalid_data(
    local_gcp, write_gridmap, cn, auth_client
):
    write_gridmap(
        f'"/C=US/O=Globus Consortium/OU=Globus Connect User/CN={cn}" sirosen\n'
    )
    assert local_gcp.get_owner_info() == (f"{cn}@globusid.org", False)


@pytest.mark.parametrize(
    "bad_cn_line",
    [
        '"/C=US/O=Globus Consortium/OU=Globus Connect User/CN=sirosen"',
        '"/C=US/O=Globus Consortium/OU=Globus Connect User/CN=sirosen" sirosen sirosen',
        "",
        '"" sirosen',
    ],
)
def test_get_owner_info_malformed_entry(local_gcp, write_gridmap, bad_cn_line):
    write_gridmap(bad_cn_line + "\n")
    assert local_gcp.get_owner_info() is None


def test_get_owner_info_no_conf(local_gcp):
    assert local_gcp.get_owner_info() is None
    assert local_gcp.get_owner_info(auth_client) is None


def test_get_owner_info_no_confdir(local_gcp, mocked_confdir, auth_client):
    shutil.rmtree(mocked_confdir)
    assert local_gcp.get_owner_info() is None
    assert local_gcp.get_owner_info(auth_client) is None


def test_get_owner_info_multiline_data(local_gcp, write_gridmap, auth_client):
    write_gridmap(
        "\n".join(
            [
                f'"/C=US/O=Globus Consortium/OU=Globus Connect User/CN=sirosen{x}" sirosen{x}'  # noqa: E501
                for x in ["", "2", "3"]
            ]
        )
        + "\n"
    )
    assert local_gcp.get_owner_info() == ("sirosen@globusid.org", False)

    register_api_route(
        "auth",
        "/v2/api/identities",
        json={
            "identities": [
                {
                    "email": "sirosen@globus.org",
                    "id": "ae332d86-d274-11e5-b885-b31714a110e9",
                    "identity_provider": "41143743-f3c8-4d60-bbdb-eeecaba85bd9",
                    "identity_type": "login",
                    "name": "Stephen Rosen",
                    "organization": "Globus Team",
                    "status": "used",
                    "username": "sirosen@globusid.org",
                }
            ]
        },
    )
    data = local_gcp.get_owner_info(auth_client)
    assert isinstance(data, dict)
    assert data["id"] == "ae332d86-d274-11e5-b885-b31714a110e9"


def test_get_owner_info_no_auth_data(local_gcp, write_gridmap, auth_client):
    write_gridmap(
        '"/C=US/O=Globus Consortium/OU=Globus Connect User/CN=sirosen" sirosen\n'
    )
    assert local_gcp.get_owner_info() == ("sirosen@globusid.org", False)

    register_api_route("auth", "/v2/api/identities", json={"identities": []})
    data = local_gcp.get_owner_info(auth_client)
    assert data is None


def test_get_owner_info_gridmap_permission_denied(local_gcp, mocked_confdir):
    fpath = os.path.join(mocked_confdir, "gridmap")
    with open(fpath, "w"):  # "touch"
        pass
    os.chmod(fpath, 0o000)

    with pytest.raises(OSError) as excinfo:
        local_gcp.get_owner_info()
    # permission denied
    assert excinfo.value.errno == 13


def test_get_endpoint_id_permission_denied(local_gcp, mocked_confdir):
    fpath = os.path.join(mocked_confdir, "client-id.txt")
    with open(fpath, "w"):  # "touch"
        pass
    os.chmod(fpath, 0o000)

    with pytest.raises(OSError) as excinfo:
        local_gcp.endpoint_id
    # permission denied
    assert excinfo.value.errno == 13
