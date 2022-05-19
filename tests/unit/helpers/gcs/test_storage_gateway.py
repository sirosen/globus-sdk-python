import pytest

from globus_sdk import (
    ActiveScaleStoragePolicies,
    AzureBlobStoragePolicies,
    BlackPearlStoragePolicies,
    BoxStoragePolicies,
    CephStoragePolicies,
    GoogleCloudStoragePolicies,
    GoogleDriveStoragePolicies,
    HPSSStoragePolicies,
    IrodsStoragePolicies,
    OneDriveStoragePolicies,
    POSIXStagingStoragePolicies,
    POSIXStoragePolicies,
    S3StoragePolicies,
    StorageGatewayDocument,
)


@pytest.mark.parametrize(
    "use_kwargs,doc_version",
    [
        ({}, "1.0.0"),
        ({"require_mfa": True}, "1.1.0"),
        ({"require_mfa": False}, "1.1.0"),
    ],
)
def test_datatype_version_deduction(use_kwargs, doc_version):
    sg = StorageGatewayDocument(**use_kwargs)
    assert sg["DATA_TYPE"] == f"storage_gateway#{doc_version}"


def test_storage_gateway_policy_document_conversion():
    policies = POSIXStoragePolicies(
        groups_allow=["jedi", "wookies"], groups_deny=["sith", "stormtroopers"]
    )
    sg = StorageGatewayDocument(policies=policies)
    assert "policies" in sg
    assert isinstance(sg["policies"], dict)
    assert sg["policies"] == {
        "DATA_TYPE": "posix_storage_policies#1.0.0",
        "groups_allow": ["jedi", "wookies"],
        "groups_deny": ["sith", "stormtroopers"],
    }


def test_posix_staging_env_vars():
    p = POSIXStagingStoragePolicies(
        groups_allow=("vulcans", "starfleet"),
        groups_deny=(x for x in ("ferengi", "romulans")),
        stage_app="/globus/bin/posix-stage-data",
        environment=({"name": "VOLUME", "value": "/vol/0"},),
    )

    assert isinstance(p["environment"], list)
    assert dict(p) == {
        "DATA_TYPE": "posix_staging_storage_policies#1.0.0",
        "groups_allow": ["vulcans", "starfleet"],
        "groups_deny": ["ferengi", "romulans"],
        "stage_app": "/globus/bin/posix-stage-data",
        "environment": [{"name": "VOLUME", "value": "/vol/0"}],
    }


@pytest.mark.parametrize(
    "doc_class",
    [
        StorageGatewayDocument,
        POSIXStagingStoragePolicies,
        POSIXStoragePolicies,
        BlackPearlStoragePolicies,
        BoxStoragePolicies,
        CephStoragePolicies,
        GoogleDriveStoragePolicies,
        GoogleCloudStoragePolicies,
        OneDriveStoragePolicies,
        AzureBlobStoragePolicies,
        S3StoragePolicies,
        ActiveScaleStoragePolicies,
        IrodsStoragePolicies,
        HPSSStoragePolicies,
    ],
)
def test_storage_gateway_documents_support_additional_fields(doc_class):
    d = doc_class()
    assert "DATA_TYPE" in d
    assert "foo" not in d

    d2 = doc_class(additional_fields={"foo": "bar"})
    assert "DATA_TYPE" in d2
    assert d2["foo"] == "bar"


def test_onedrive_storage_policies_tenant_is_nullable():
    doc = OneDriveStoragePolicies()
    assert "tenant" not in doc

    doc = OneDriveStoragePolicies(tenant="foo")
    assert "tenant" in doc
    assert doc["tenant"] == "foo"

    doc = OneDriveStoragePolicies(tenant=None)
    assert "tenant" in doc
    assert doc["tenant"] is None
