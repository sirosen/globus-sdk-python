Globus Connect Server API
=========================

The Globus Connect Server Manager API (GCS Manager API) runs on a
Globus Connect Server Endpoint and allows management of the Endpoint,
Storage Gateways, Collections, and other resources.

Unlike other Globus services, there is no single central API used to contact
GCS Manager instances. Therefore, the ``GCSClient`` is always initialized with
the FQDN (DNS name) of the GCS Endpoint.
e.g. ``gcs = GCSClient("abc.def.data.globus.org")``

Client
------

The primary interface for the GCS Manager API is the ``GCSClient`` class.

.. autoclass:: globus_sdk.GCSClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Client Errors
-------------

When an error occurs, a ``GCSClient`` will raise this specialized type of
error, rather than a generic ``GlobusAPIError``.

.. autoclass:: globus_sdk.GCSAPIError
   :members:
   :show-inheritance:

GCS Responses
-------------

.. automodule:: globus_sdk.services.gcs.response
   :members:
   :show-inheritance:
