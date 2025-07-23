Globus Compute
==============

.. currentmodule:: globus_sdk

The standard way to interact with the Globus Compute service is through the
`Globus Compute SDK <https://globus-compute.readthedocs.io/en/stable/sdk.html>`_,
a separate, specialized toolkit that offers enhanced functionality for Globus Compute.
Under the hood, the Globus Compute SDK uses the following clients to interact with
the Globus Compute API. Advanced users may choose to work directly with these clients
for custom implementations.

There are two client classes, supporting versions 2 and 3 of the Globus Compute
API.
Where feasible, new projects should use :class:`ComputeClientV3`, which
supports the latest API features and improvements.

..  autoclass:: ComputeClientV2
    :members:
    :member-order: bysource
    :show-inheritance:
    :exclude-members: error_class, scopes

    ..  attribute:: scopes

        ..  listknownscopes:: globus_sdk.scopes.ComputeScopes
            :base_name: ComputeClientV2.scopes

..  autoclass:: ComputeClientV3
    :members:
    :member-order: bysource
    :show-inheritance:
    :exclude-members: error_class, scopes

    ..  attribute:: scopes

        ..  listknownscopes:: globus_sdk.scopes.ComputeScopes
            :base_name: ComputeClientV3.scopes


..  py:class:: ComputeClient

    A deprecated alias for :class:`ComputeClientV2`.

    ..  warning::

        This class will be removed in ``globus-sdk`` version 4.
        Users should migrate to one of the explicitly-versioned classes.

Client Errors
-------------

When an API error occurs, :class:`ComputeClientV2` and :class:`ComputeClientV3`
will raise ``ComputeAPIError``.

.. autoclass:: ComputeAPIError
   :members:
   :show-inheritance:
