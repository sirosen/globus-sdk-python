.. _local_endpoints:

Local Endpoints
===============

Unlike SDK functionality for accessing Globus APIs, the locally available
Globus Endpoints require special treatment.
These accesses are not authenticated via Globus Auth, and may rely upon the
state of the local filesystem, running processes, and the permissions of local
users.

Globus Connect Server
---------------------

There are no SDK methods for accessing an installation of Globus Connect
Server.

Globus Connect Personal
-----------------------

Globus Connect Personal endpoints belonging to the current user may be accessed
via instances of the following class:


.. autoclass:: globus_sdk.LocalGlobusConnectPersonal
   :members:
   :member-order: bysource
