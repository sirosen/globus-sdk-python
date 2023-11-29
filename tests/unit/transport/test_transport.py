import pathlib

import pytest

from globus_sdk.transport import RequestsTransport, RetryContext
from globus_sdk.transport.requests import _exponential_backoff


def _linear_backoff(ctx: RetryContext) -> float:
    if ctx.backoff is not None:
        return ctx.backoff
    return 0.5 * (2**ctx.attempt)


ca_bundle_file = pathlib.Path(__file__).parent.parent.absolute() / "CA-Bundle.cert"
ca_bundle_directory = ca_bundle_file.parent
ca_bundle_non_existent = ca_bundle_directory / "bogus.bogus"


@pytest.mark.parametrize(
    "param_name, init_value, tune_value",
    [
        ("verify_ssl", True, True),
        ("verify_ssl", True, False),
        ("verify_ssl", True, ca_bundle_file),
        ("verify_ssl", True, str(ca_bundle_file)),
        ("verify_ssl", True, ca_bundle_directory),
        ("verify_ssl", True, str(ca_bundle_directory)),
        ("verify_ssl", True, ca_bundle_non_existent),
        ("verify_ssl", True, str(ca_bundle_non_existent)),
        ("http_timeout", 60, 120),
        ("retry_backoff", _exponential_backoff, _linear_backoff),
        ("max_sleep", 10, 10),
        ("max_sleep", 10, 1),
        ("max_retries", 0, 5),
        ("max_retries", 10, 0),
    ],
)
def test_transport_tuning(param_name, init_value, tune_value):
    expected_value = (
        str(tune_value) if isinstance(tune_value, pathlib.Path) else tune_value
    )
    init_kwargs = {param_name: init_value}
    transport = RequestsTransport(**init_kwargs)

    assert getattr(transport, param_name) == init_value

    tune_kwargs = {param_name: tune_value}
    with transport.tune(**tune_kwargs):
        assert getattr(transport, param_name) == expected_value

    assert getattr(transport, param_name) == init_value
