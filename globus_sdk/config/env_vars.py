"""
Definition and loading of standard environment variables, plus a wrappers for loading
and parsing values.
"""
import logging
import os
import typing
from distutils.util import strtobool

log = logging.getLogger(__name__)


ENVNAME_VAR = "GLOBUS_SDK_ENVIRONMENT"
HTTP_TIMEOUT_VAR = "GLOBUS_SDK_HTTP_TIMEOUT"
SSL_VERIFY_VAR = "GLOBUS_SDK_VERIFY_SSL"


def _load_var(varname: str, default, explicit_value=None, cast=None):
    # use the explicit value if given and non-None, otherwise, do an env lookup
    value = (
        explicit_value if explicit_value is not None else os.getenv(varname, default)
    )
    if cast:
        value = cast(value, default)
    # only info log on non-default *values*
    # meaning that if we define the default as 'foo' and someone explicitly sets 'foo',
    # no info log gets emitted
    if value != default:
        log.info(f"on lookup, non-default setting: {varname}={value}")
    else:
        log.debug(f"on lookup, default setting: {varname}={value}")
    return value


def _bool_cast(value: typing.Any, default) -> bool:
    if isinstance(value, bool):
        return value
    return strtobool(value.lower())


def _optfloat_cast(value: typing.Any, default) -> typing.Optional[float]:
    try:
        return float(value)
    except ValueError:
        pass
    if value == "":
        return typing.cast(float, default)
    log.error(f'Value "{value}" can\'t cast to optfloat')
    raise ValueError(f"Invalid config float: {value}")


def get_environment_name(inputenv: typing.Optional[str] = None) -> str:
    return typing.cast(
        str, _load_var(ENVNAME_VAR, "production", explicit_value=inputenv)
    )


def get_ssl_verify(value: typing.Optional[bool] = None) -> bool:
    return typing.cast(
        bool, _load_var(SSL_VERIFY_VAR, True, explicit_value=value, cast=_bool_cast)
    )


def get_http_timeout(value: typing.Optional[float] = None) -> typing.Optional[float]:
    ret = typing.cast(
        typing.Optional[float],
        _load_var(HTTP_TIMEOUT_VAR, 60.0, explicit_value=value, cast=_optfloat_cast),
    )
    if ret == -1.0:
        return None
    return ret
