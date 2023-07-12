Auth Requirements Errors
========================

Globus Auth Requirements Error is a response format that conveys to a client any
modifications to a session (i.e., "boosting") that will be required
to complete a particular request.

The ``auth_requirements_error`` module provides a number of tools to make it easier to
identify and handle these errors when they occur.

GlobusAuthRequirementsError
---------------------------

The ``GlobusAuthRequirementsError`` class provides a model for working with Globus
Auth Requirements Error responses in the Python SDK. The shape of an instance closely
matches that of the JSON response, such that in order to access a
response's required_scopes one could use, e.g.,:

.. code-block:: python

    from globus_sdk.experimental import auth_requirements_error

    error = auth_requirements_error.GlobusAuthRequirementsError(response)
    error.authorization_parameters.required_scopes

``GlobusAuthRequirementsError`` enforces types strictly when parsing a Globus
Auth Requirements Error response dictionary, and will raise a ``ValueError`` if a
supported field is supplied with a value of the wrong type.
``GlobusAuthRequirementsError`` does not, however, attempt to mimic or itself enforce
any logic specific to the Globus Auth service with regard to what represents a coherent
combination of fields (e.g., that ``session_required_mfa`` requires either
``session_required_identities`` or ``session_required_single_domain``
in order to be properly handled).

If you are writing a service that needs to respond with a Globus Auth Requirements Error, you can
instantiate the ``GlobusAuthRequirementsError`` class directly to emit auth requirements errors
in your application, e.g.:

.. code-block:: python

    from globus_sdk.experimental import auth_requirements_error

    error = auth_requirements_error.GlobusAuthRequirementsError(
        code="ConsentRequired",
        authorization_parameters=GlobusAuthorizationParameters(
            required_scopes=["urn:globus:auth:scope:transfer.api.globus.org"],
            session_message="Missing required 'foo' consent",
        ),
    )

    # Render a strict dictionary
    error.to_dict()

If non-canonical fields are supplied on creation (either as keyword arguments
during instantiation or as fields in a dictionary supplied to ``from_dict()``),
you can preserve these fields in the rendered output dictionary
by specifying ``include_extra=True``.

.. code-block:: python

    from globus_sdk.experimental import auth_requirements_error

    error = auth_requirements_error.GlobusAuthRequirementsError(
        code="ConsentRequired",
        message="Missing required 'foo' consent",
        request_id="WmMV97A1w",
        required_scopes=["urn:globus:auth:scope:transfer.api.globus.org:all[*foo]"],
        resource="/transfer",
        authorization_parameters=GlobusAuthorizationParameters(
            required_scopes=["urn:globus:auth:scope:transfer.api.globus.org"],
            session_message="Missing required 'foo' consent",
        ),
    )

    # Render a dictionary with extra fields
    error.to_dict(include_extra=True)

These fields are stored by both the ``GlobusAuthRequirementsError`` and
``GlobusAuthenticationParameters`` classes in an ``extra_fields``
attribute.

Parsing Responses
-----------------

If you are writing a client to a Globus API, the ``auth_requirements_error`` subpackage
provides utilities to detect legacy auth requirements error response
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

    If a GlobusAPIError represents multiple errors that were returned in an
    array, this only returns the first error in that array that can be
    converted to the Globus Auth Requirements Error response format. In this case (and,
    in general) it's preferable to use ``to_auth_requirements_errors()`` (which also
    accepts a list of ``GlobusAPIError``\ s, ``ErrorSubdocument``\ s, and JSON
    response dictionaries):

.. code-block:: python

    auth_requirements_error.utils.to_auth_requirements_error(
        other_error
    )  # GlobusAuthRequirementsError
    auth_requirements_error.utils.to_auth_requirements_errors(
        [other_error]
    )  # [GlobusAuthRequirementsError, ...]
