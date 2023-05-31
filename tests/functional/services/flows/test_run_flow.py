from __future__ import annotations

import pytest

from globus_sdk import FlowsAPIError, SpecificFlowClient
from globus_sdk._testing import load_response


def test_run_flow(specific_flow_client_class: type[SpecificFlowClient]):
    metadata = load_response(SpecificFlowClient.run_flow).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    resp = flow_client.run_flow(**metadata["request_params"])
    assert resp.http_status == 200


def test_run_flow_missing_scope(specific_flow_client_class: type[SpecificFlowClient]):
    metadata = load_response(
        SpecificFlowClient.run_flow, case="missing_scope_error"
    ).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    with pytest.raises(FlowsAPIError) as excinfo:
        flow_client.run_flow(**metadata["request_params"])

    err = excinfo.value
    assert err.http_status == 403
    assert err.code == "MISSING_SCOPE"
    assert (
        err.message == "This action requires the following scope: frobulate[demuddle]"
    )
