"""
Definition and loading of standard environment variables, plus a wrappers for loading
and parsing values.
"""
import logging
import os
import typing

log = logging.getLogger(__name__)


ENVNAME_VAR = "GLOBUS_SDK_ENVIRONMENT"
HTTP_TIMEOUT_VAR = "GLOBUS_SDK_HTTP_TIMEOUT"
SSL_VERIFY_VAR = "GLOBUS_SDK_VERIFY_SSL"


def _load_var(
    varname: str, default: str, explicit_value: typing.Optional[str] = None
) -> str:
    # use the explicit value if given and non-None, otherwise, do an env lookup
    value = (
        explicit_value if explicit_value is not None else os.getenv(varname, default)
    )
    # only info log on non-default *values*
    # meaning that if we define the default as 'foo' and someone explicitly sets 'foo',
    # no info log gets emitted
    if value != default:
        log.info(f"on lookup, non-default setting: {varname}={value}")
    else:
        log.debug(f"on lookup, default setting: {varname}={value}")
    return value


def _bool_cast(value: str) -> bool:
    value = value.lower()
    if value in ("1", "yes", "true", "on"):
        return True
    elif value in ("0", "no", "false", "off"):
        return False
    log.error(f'Value "{value}" can\'t cast to bool')
    raise ValueError(f"Invalid config bool: {value}")


def _optfloat_cast(value: str) -> typing.Optional[float]:
    try:
        return float(value)
    except ValueError:
        pass
    if value == "":
        return None
    log.error(f'Value "{value}" can\'t cast to optfloat')
    raise ValueError(f"Invalid config float: {value}")


def get_environment_name(inputenv: typing.Optional[str] = None) -> str:
    return _load_var(ENVNAME_VAR, "production", explicit_value=inputenv)


def get_ssl_verify(value: typing.Optional[bool] = None) -> bool:
    if isinstance(value, bool):
        return value
    return _bool_cast(_load_var(SSL_VERIFY_VAR, "true"))


def get_http_timeout(value: typing.Optional[float] = None) -> typing.Optional[float]:
    if value is not None:
        return value
    return _optfloat_cast(_load_var(HTTP_TIMEOUT_VAR, "60"))
