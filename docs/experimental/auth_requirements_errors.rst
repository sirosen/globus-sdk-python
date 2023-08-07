Auth Requirements Errors
========================

Globus Auth Requirements Error is a response format that conveys to a client any
modifications to a session (i.e., "boosting") that will be required
to complete a particular request.

The ``globus_sdk.experimental.auth_requirements_error`` module provides a
number of tools to make it easier to identify and handle these errors when they occur.

GlobusAuthRequirementsError
---------------------------

The ``GlobusAuthRequirementsError`` class provides a model for working with Globus
Auth Requirements Error responses.

Services in the Globus ecosystem may need to communicate authorization requirements
to their consumers. For example, a service may need to instruct clients to have the user
consent to an additional scope, ``"foo"``. In such a case, ``GlobusAuthRequirementsError``
can provide serialization into the well-known Globus Auth Requirements Error format:

.. code-block:: python

    from globus_sdk.experimental.auth_requirements_error import GlobusAuthRequirementsError

    error = GlobusAuthRequirementsError(
        code="ConsentRequired",
        authorization_parameters=GlobusAuthorizationParameters(
            required_scopes=["foo"],
            session_message="Missing required 'foo' consent",
        ),
    )

    # Render a strict dictionary
    error.to_dict()

If non-canonical fields are needed, the ``extra`` argument can be used to
supply a dictionary of additional fields to include. Non-canonical fields present
in the provided dictionary when calling ``from_dict()`` are stored similarly.
You can include these fields in the rendered output dictionary
by specifying ``include_extra=True`` when calling ``to_dict()``.

.. code-block:: python

    from globus_sdk.experimental.auth_requirements_error import GlobusAuthRequirementsError

    error = GlobusAuthRequirementsError(
        code="ConsentRequired",
        authorization_parameters=GlobusAuthorizationParameters(
            required_scopes=["foo"],
            session_message="Missing required 'foo' consent",
        ),
        extra={
            "message": "Missing required 'foo' consent",
            "request_id": "WmMV97A1w",
            "required_scopes": ["foo"],
            "resource": "/transfer",
        },
    )

    # Render a dictionary with extra fields
    error.to_dict(include_extra=True)

These fields are stored by both the ``GlobusAuthRequirementsError`` and
``GlobusAuthenticationParameters`` classes in an ``extra`` attribute.

.. note::

    Non-canonical fields in a Globus Auth Requirements Error are primarily intended
    to make it easier for services to provide backward-compatibile error responses
    to clients that have not adopted the Globus Auth Requirements Error format. Avoid
    using non-canonical fields for any data that should be generically understood by
    a consumer of the error response.

Parsing Responses
-----------------

If you are writing a client to a Globus API, the ``auth_requirements_error`` subpackage
provides utilities to detect legacy Globus Auth requirements error response
formats and normalize them.

To detect if a ``GlobusAPIError``, ``ErrorSubdocument``, or JSON response
dictionary represents an error that can be converted to a Globus Auth
Requirements Error, you can use, e.g.,:

.. code-block:: python

    from globus_sdk.experimental import auth_requirements_error

    error_dict = {
        "code": "ConsentRequired",
        "message": "Missing required foo consent",
    }
    # The dict is not a Globus Auth Requirements Error, so `False` is returned.
    auth_requirements_error.utils.is_auth_requirements_error(error_dict)

    # The dict is not a Globus Auth Requirements Error and cannot be converted.
    auth_requirements_error.utils.to_auth_requirements_error(error_dict)  # None

    error_dict = {
        "code": "ConsentRequired",
        "message": "Missing required foo consent",
        "required_scopes": ["urn:globus:auth:scope:transfer.api.globus.org:all[*foo]"],
    }
    auth_requirements_error.utils.is_auth_requirements_error(error_dict)  # True
    auth_requirements_error.utils.to_auth_requirements_error(
        error_dict
    )  # GlobusAuthRequirementsError

.. note::

    If a ``GlobusAPIError`` represents multiple errors that were returned in an
    array, ``to_auth_requirements_error()`` only returns the first error in that
    array that can be converted to the Globus Auth Requirements Error response format.
    In this case (and in general) it's preferable to use
    ``to_auth_requirements_errors()`` (which also accepts a list of
    ``GlobusAPIError``\ s, ``ErrorSubdocument``\ s, and JSON response dictionaries):

.. code-block:: python

    auth_requirements_error.utils.to_auth_requirements_error(
        other_error
    )  # GlobusAuthRequirementsError
    auth_requirements_error.utils.to_auth_requirements_errors(
        [other_error]
    )  # [GlobusAuthRequirementsError, ...]

Notes
-----

``GlobusAuthRequirementsError`` enforces types strictly when parsing a Globus
Auth Requirements Error response dictionary, and will raise a ``ValueError`` if a
supported field is supplied with a value of the wrong type.

``GlobusAuthRequirementsError`` does not attempt to mimic or itself enforce
any logic specific to the Globus Auth service with regard to what represents a valid
combination of fields (e.g., ``session_required_mfa`` requires either
``session_required_identities`` or ``session_required_single_domain``
in order to be properly handled).
