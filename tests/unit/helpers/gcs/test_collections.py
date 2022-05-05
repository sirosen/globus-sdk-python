import uuid

import pytest

from globus_sdk import (
    CollectionDocument,
    GuestCollectionDocument,
    MappedCollectionDocument,
)

STUB_SG_ID = uuid.uuid1()  # storage gateway
STUB_MC_ID = uuid.uuid1()  # mapped collection
STUB_UC_ID = uuid.uuid1()  # user credential


def test_collection_base_abstract():
    with pytest.raises(TypeError):
        CollectionDocument()


def test_collection_type_field():
    m = MappedCollectionDocument(
        storage_gateway_id=STUB_SG_ID, collection_base_path="/"
    )
    g = GuestCollectionDocument(
        mapped_collection_id=STUB_MC_ID,
        user_credential_id=STUB_UC_ID,
        collection_base_path="/",
    )
    assert m["collection_type"] == "mapped"
    assert g["collection_type"] == "guest"


@pytest.mark.parametrize(
    "use_kwargs,doc_version",
    [
        ({}, "1.0.0"),
        ({"user_message_link": "https://example.net/"}, "1.1.0"),
        ({"user_message": "kthxbye"}, "1.1.0"),
        ({"user_message": ""}, "1.1.0"),
        ({"enable_https": True}, "1.1.0"),
        ({"enable_https": False}, "1.1.0"),
    ],
)
def test_datatype_version_deduction(use_kwargs, doc_version):
    m = MappedCollectionDocument(**use_kwargs)
    assert m["DATA_TYPE"] == f"collection#{doc_version}"
    g = GuestCollectionDocument(**use_kwargs)
    assert g["DATA_TYPE"] == f"collection#{doc_version}"


@pytest.mark.parametrize(
    "use_kwargs,doc_version",
    [
        ({"sharing_users_allow": "sirosen"}, "1.2.0"),
        ({"sharing_users_allow": ["sirosen", "aaschaer"]}, "1.2.0"),
        ({"sharing_users_deny": "sirosen"}, "1.2.0"),
        ({"sharing_users_deny": ["sirosen", "aaschaer"]}, "1.2.0"),
        ({"force_verify": True}, "1.4.0"),
        ({"force_verify": False}, "1.4.0"),
        ({"disable_anonymous_writes": True}, "1.5.0"),
        ({"disable_anonymous_writes": False}, "1.5.0"),
    ],
)
def test_datatype_version_deduction_mapped_specific_fields(use_kwargs, doc_version):
    d = MappedCollectionDocument(**use_kwargs)
    assert d["DATA_TYPE"] == f"collection#{doc_version}"


def test_datatype_version_deduction_add_custom(monkeypatch):
    custom_field = "foo-made-up-field"
    monkeypatch.setitem(
        CollectionDocument.DATATYPE_VERSION_IMPLICATIONS, custom_field, (1, 20, 0)
    )

    m = MappedCollectionDocument(
        storage_gateway_id=STUB_SG_ID,
        collection_base_path="/",
        additional_fields={custom_field: "foo"},
    )
    assert m["DATA_TYPE"] == "collection#1.20.0"
    g = GuestCollectionDocument(
        mapped_collection_id=STUB_MC_ID,
        user_credential_id=STUB_UC_ID,
        collection_base_path="/",
        additional_fields={custom_field: "foo"},
    )
    assert g["DATA_TYPE"] == "collection#1.20.0"
