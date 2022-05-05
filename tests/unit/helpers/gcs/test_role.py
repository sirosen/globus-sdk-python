from globus_sdk import GCSRoleDocument


def test_gcs_role_helper_supports_additional_fields():
    r = GCSRoleDocument()
    assert r["DATA_TYPE"] == "role#1.0.0"
    assert "foo" not in r

    r2 = GCSRoleDocument(additional_fields={"foo": "bar"})
    assert r2["DATA_TYPE"] == "role#1.0.0"
    assert r2["foo"] == "bar"
