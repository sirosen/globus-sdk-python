from globus_sdk import GCSClient


def test_client_address_handling():
    # variants of the same location
    c1 = GCSClient("foo.data.globus.org")
    c2 = GCSClient("https://foo.data.globus.org")
    c3 = GCSClient("https://foo.data.globus.org/api")
    c4 = GCSClient("https://foo.data.globus.org/api/")
    # explicit subpath of /api/
    c5 = GCSClient("https://foo.data.globus.org/api/bar")
    # explicit construction can point at the root (rather than /api/)
    c6 = GCSClient("foo.data.globus.org")
    c6.base_url = "https://foo.data.globus.org/"

    # 1, 2, 3, and 4 are all the same
    assert c1.base_url == c2.base_url
    assert c1.base_url == c3.base_url
    assert c1.base_url == c4.base_url

    # 5 and 6 are different from the rest
    assert c5.base_url != c1.base_url
    assert c6.base_url != c1.base_url

    # 6 is the root of 1
    assert c1.base_url.startswith(c6.base_url)


def test_gcs_client_has_no_resource_server():
    c = GCSClient("foo.data.globus.org")
    assert c.resource_server is None
