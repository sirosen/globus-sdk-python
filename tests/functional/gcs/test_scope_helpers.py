import uuid

zero_id = uuid.UUID(int=0)
zero_id_s = str(zero_id)


def test_manage_collections_scope_helper(client):
    sb = client.get_gcs_endpoint_scopes(zero_id)
    assert (
        sb.manage_collections == f"urn:globus:auth:scope:{zero_id_s}:manage_collections"
    )
    # data_access is separated from endpoint scopes
    assert not hasattr(sb, "data_access")


def test_data_access_scope_helper(client):
    sb = client.get_gcs_collection_scopes(zero_id)
    assert sb.data_access == f"https://auth.globus.org/scopes/{zero_id_s}/data_access"
    # manage_collections is separated from collection scopes
    assert not hasattr(sb, "manage_collections")
