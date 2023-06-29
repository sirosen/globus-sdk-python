import typing as t
from contextlib import suppress

from globus_sdk.exc import ErrorSubdocument, GlobusAPIError

from .session_error import GlobusSessionError
from .variants import (
    LegacyAuthorizationParametersError,
    LegacyConsentRequiredAPError,
    LegacyConsentRequiredTransferError,
)


def to_session_error(
    error: t.Union[GlobusAPIError, ErrorSubdocument, t.Dict]
) -> t.Optional[GlobusSessionError]:
    """
    Converts a GlobusAPIError, ErrorSubdocument, or dict into a GlobusSessionError by
    attempting to match to GlobusSessionError (preferred) or legacy variants.

    .. note::
        a GlobusAPIError may contain multiple errors, and in this case only a single
        session error is returned for the first error that matches a known format.


    If the provided error does not match a known format, None is returned.

    :param error: The error to convert.
    :type error: a GlobusAPIError, ErrorSubdocument, or dict
    """

    # GlobusAPIErrors may contain more than one error, so we consider all of them
    # even though we only return the first.
    if isinstance(error, GlobusAPIError):
        # Iterate over ErrorSubdocuments
        for subdoc in error.errors:
            session_error = to_session_error(subdoc)
            if session_error is not None:
                # Return only the first session error we encounter
                return session_error
        # We failed to find a session error
        return None
    elif isinstance(error, ErrorSubdocument):
        error_dict = error.raw
    else:
        error_dict = error

    # Prefer a proper session error, if possible
    with suppress(ValueError):
        return GlobusSessionError.from_dict(error_dict)

    for variant in [
        LegacyAuthorizationParametersError,
        LegacyConsentRequiredTransferError,
        LegacyConsentRequiredAPError,
    ]:
        with suppress(ValueError):
            return variant.from_dict(error_dict).to_session_error()

    return None


def to_session_errors(
    errors: t.List[t.Union[GlobusAPIError, ErrorSubdocument, t.Dict]]
) -> t.List[GlobusSessionError]:
    """
    Converts a list of GlobusAPIErrors, ErrorSubdocuments, or dicts into a list of
    GlobusSessionErrors by attempting to match each error to
    GlobusSessionError (preferred) or legacy variants.

    .. note::
        A GlobusAPIError may contain multiple errors, so the result
        list could be longer than the provided list.

    If no errors match any known formats, an empty list is returned.

    :param errors: The errors to convert.
    :type errors: a list of GlobusAPIErrors, ErrorSubdocuments, or dicts
    """
    candidate_errors = []
    for error in errors:
        if isinstance(error, GlobusAPIError):
            # Use the ErrorSubdocuments
            candidate_errors.extend(error.errors)
        else:
            candidate_errors.append(error)

    # Try to convert all candidate errors to session errors
    all_errors = [to_session_error(error) for error in candidate_errors]

    # Remove any errors that did not resolve to a session error
    return [error for error in all_errors if error is not None]


def is_session_error(error: t.Union[GlobusAPIError, ErrorSubdocument, t.Dict]) -> bool:
    """
    Return True if the provided error matches a known session error format.

    :param error: The error to check.
    :type error: a GlobusAPIError, ErrorSubdocument, or dict
    """
    return to_session_error(error) is not None


def has_session_errors(
    errors: t.List[t.Union[GlobusAPIError, ErrorSubdocument, t.Dict]]
) -> bool:
    """
    Return True if any of the provided errors match a known session error format.

    :param errors: The errors to check.
    :type errors: a list of GlobusAPIErrors, ErrorSubdocuments, or dicts
    """
    return any(is_session_error(error) for error in errors)
