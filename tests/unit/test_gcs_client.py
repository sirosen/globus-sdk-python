from globus_sdk import GCSClient


def test_client_address_handling():
    # check on address parsing abilities
    c1 = GCSClient("foo.data.globus.org")
    c2 = GCSClient("https://foo.data.globus.org")
    c3 = GCSClient("https://foo.data.globus.org/api")

    assert c1.base_url == c3.base_url
    assert c2.base_url != c1.base_url
    assert c1.base_url.startswith(c2.base_url)


def test_gcs_client_has_no_resource_server():
    c = GCSClient("foo.data.globus.org")
    assert c.resource_server is None
