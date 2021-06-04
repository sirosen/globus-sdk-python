from globus_sdk import exc
from globus_sdk.base import BaseClient


class GroupsClient(BaseClient):
    """
    Client for the
    `Globus Groups API <https://docs.globus.org/api/groups/>`_.

    .. automethodlist:: globus_sdk.GroupsClient
    """

    error_class = exc.GroupsAPIError
    service_name = "groups"
