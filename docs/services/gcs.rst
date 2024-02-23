Globus Connect Server API
=========================

.. currentmodule:: globus_sdk

The Globus Connect Server Manager API (GCS Manager API) runs on a
Globus Connect Server Endpoint and allows management of the Endpoint,
Storage Gateways, Collections, and other resources.

Unlike other Globus services, there is no single central API used to contact
GCS Manager instances. Therefore, the :class:`GCSClient` is always initialized with
the FQDN (DNS name) of the GCS Endpoint.
e.g. ``gcs = GCSClient("abc.def.data.globus.org")``

Client
------

The primary interface for the GCS Manager API is the :class:`GCSClient` class.

.. autoclass:: GCSClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

.. autoclass:: EndpointDocument
   :members:
   :show-inheritance:

.. autoclass:: GCSRoleDocument
   :members:
   :show-inheritance:

.. autoclass:: StorageGatewayDocument
   :members:
   :show-inheritance:

.. autoclass:: UserCredentialDocument
   :members:
   :show-inheritance:

Collections
~~~~~~~~~~~

.. autoclass:: CollectionDocument
   :members:
   :show-inheritance:

.. autoclass:: MappedCollectionDocument
   :members:
   :show-inheritance:

.. autoclass:: GuestCollectionDocument
   :members:
   :show-inheritance:

Storage Gateway Policies
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: StorageGatewayPolicies
   :members:
   :show-inheritance:

.. autoclass:: ActiveScaleStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: AzureBlobStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: BlackPearlStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: BoxStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: CephStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: CollectionPolicies
   :members:
   :show-inheritance:

.. autoclass:: GoogleCloudStorageCollectionPolicies
   :members:
   :show-inheritance:

.. autoclass:: GoogleCloudStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: GoogleDriveStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: HPSSStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: IrodsStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: OneDriveStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: POSIXCollectionPolicies
   :members:
   :show-inheritance:

.. autoclass:: POSIXStagingCollectionPolicies
   :members:
   :show-inheritance:

.. autoclass:: POSIXStagingStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: POSIXStoragePolicies
   :members:
   :show-inheritance:

.. autoclass:: S3StoragePolicies
   :members:
   :show-inheritance:

Client Errors
-------------

When an error occurs, a :class:`GCSClient` will raise this specialized type of
error, rather than a generic :class:`GlobusAPIError`.

.. autoclass:: GCSAPIError
   :members:
   :show-inheritance:

GCS Responses
-------------

.. autoclass:: IterableGCSResponse
   :members:
   :show-inheritance:

.. autoclass:: UnpackingGCSResponse
   :members:
   :show-inheritance:
