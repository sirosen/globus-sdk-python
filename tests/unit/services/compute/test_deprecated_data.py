import pytest

from globus_sdk.exc import RemovedInV4Warning
from globus_sdk.services.compute.data import (
    ComputeFunctionDocument,
    ComputeFunctionMetadata,
)


def test_compute_function_metadata_deprecated():
    with pytest.warns(
        RemovedInV4Warning, match="ComputeFunctionMetadata is deprecated."
    ):
        ComputeFunctionMetadata()


def test_compute_function_document_deprecated():
    with pytest.warns(
        RemovedInV4Warning, match="ComputeFunctionDocument is deprecated."
    ):
        ComputeFunctionDocument(function_name="foo", function_code="bar")
