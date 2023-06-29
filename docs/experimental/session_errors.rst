Session Errors
==============

Globus Session Error is a response format that conveys to a client any
modifications to a session (i.e., "boosting") that will be required
in order to complete a particular request.

The ``session_errors`` module provides a number of tools to make it easier to
identify and handle these errors when they occur.

GlobusSessionError
------------------

The ``GlobusSessionError`` class provides a model for working with Globus
Session Error responses in the Python SDK. The shape of an instance closely
matches that of the JSON response, such that in order to access a
response's session_required_scopes one could use, e.g.,:

.. code-block:: python

    from globus_sdk.experimental import session_errors

    error = session_errors.GlobusSessionError(response)
    error.authorization_parameters.session_required_scopes

``GlobusSessionError`` enforces types strictly when parsing a Globus Session
Error response dictionary, and will raise a ``ValueError`` if a supported
field is supplied with value of the wrong type. ``GlobusSessionError`` does
not, however, attempt to mimic or itself enforce any logic specific to the
Globus Auth service with regard to what represents a coherent combination
of fields (e.g., that ``session_required_mfa`` requires either
``session_required_identities`` or ``session_required_single_domain``
in order to be properly handled).

If you are writing a service that needs to respond with a session error, you can
instantiate the ``GlobusSessionError`` class directly to emit session errors
in your application, e.g.:

.. code-block:: python

    from globus_sdk.experimental import session_errors

    error = session_errors.GlobusSessionError(
        code="ConsentRequired",
        authorization_parameters=GlobusSessionErrorAuthorizationParameters(
            session_required_scopes=["urn:globus:auth:scope:transfer.api.globus.org"],
            session_message="Missing required 'foo' consent",
        ),
    )

    # Render a strict dictionary
    error.to_dict()

If non-canonical fields were supplied on creation (either as keyword arguments
during instantiation or as fields in a dictionary supplied to ``from_dict()``),
you can preserve these fields in the rendered output dictionary
by specifying ``include_extra=True``.

.. code-block:: python

    from globus_sdk.experimental import session_errors

    error = session_errors.GlobusSessionError(
        code="ConsentRequired",
        message="Missing required 'foo' consent",
        request_id="WmMV97A1w",
        required_scopes=["urn:globus:auth:scope:transfer.api.globus.org:all[*foo]"],
        resource="/transfer",
        authorization_parameters=GlobusSessionErrorAuthorizationParameters(
            session_required_scopes=["urn:globus:auth:scope:transfer.api.globus.org"],
            session_message="Missing required 'foo' consent",
        ),
    )

    # Render a dictionary with extra fields
    error.to_dict(include_extra=True)

These fields are stored by both the ``GlobusSessionError`` and
``GlobusSessionErrorAuthenticationParameters`` classes in an ``extra_fields``
attribute.

Parsing Responses
-----------------

If you are writing a client to a Globus API, the ``session_errors`` subpackage
in the Python SDK provides utilities to detect legacy session error response
formats and normalize them.

To detect if a ``GlobusAPIError``, ``ErrorSubdocument``, or JSON response
dictionary represents an error that can be converted to a Globus Session Error,
you can use, e.g.,:

.. code-block:: python

    from globus_sdk.experimental import session_error

    error_dict = {
        "code": "ConsentRequired",
        "message": "Missing required foo consent",
    }
    session_error.utils.is_session_error(error_dict)  # False
    session_error.utils.to_session_error(error_dict)  # None

    error_dict = {
        "code": "ConsentRequired",
        "message": "Missing required foo consent",
        "required_scopes": ["urn:globus:auth:scope:transfer.api.globus.org:all[*foo]"],
    }
    session_error.utils.is_session_error(error_dict)  # True
    session_error.utils.to_session_error(error_dict)  # GlobusSessionError

.. note::
    If a GlobusAPIError represents multiple errors that were returned in an
    array, this only returns the first error in that array that can be
    converted to the Globus Session Error response format. In this case (and,
    in general) it's preferable to use ``to_session_error()`` (which also
    accepts a list of ``GlobusAPIErrors``, ``ErrorSubdocuments``, and JSON
    response dictionaries):

.. code-block:: python

    session_error.utils.to_session_error(other_error)  # GlobusSessionError
    session_error.utils.to_session_errors([other_error])  # [GlobusSessionError, ...]
