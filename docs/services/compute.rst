Globus Compute
==============

.. currentmodule:: globus_sdk

The standard way to interact with the Globus Compute service is through the
`Globus Compute SDK <https://globus-compute.readthedocs.io/en/stable/sdk.html>`_,
a separate, specialized toolkit that offers enhanced functionality for Globus Compute.
Under the hood, the Globus Compute SDK uses the following clients to interact with
the Globus Compute API. Advanced users may choose to work directly with these clients
for custom implementations.

The canonical :class:`ComputeClient` is a subclass of :class:`ComputeClientV2`,
which supports version 2 of the Globus Compute API. When feasible, new projects
should use :class:`ComputeClientV3`, which supports version 3 and includes the
latest API features and improvements.

..  autoclass:: ComputeClient
    :members:
    :member-order: bysource
    :show-inheritance:
    :exclude-members: error_class, scopes

..  autoclass:: ComputeClientV2
    :members:
    :member-order: bysource
    :show-inheritance:
    :exclude-members: error_class, scopes

    ..  attribute:: scopes

        ..  listknownscopes:: globus_sdk.scopes.ComputeScopes
            :base_name: ComputeClient.scopes

..  autoclass:: ComputeClientV3
    :members:
    :member-order: bysource
    :show-inheritance:
    :exclude-members: error_class, scopes

    ..  attribute:: scopes

        ..  listknownscopes:: globus_sdk.scopes.ComputeScopes
            :base_name: ComputeClient.scopes


Client Errors
-------------

When an error occurs, a :class:`ComputeClient` will raise a ``ComputeAPIError``.

.. autoclass:: ComputeAPIError
   :members:
   :show-inheritance:
