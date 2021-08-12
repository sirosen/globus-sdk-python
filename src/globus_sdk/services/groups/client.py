from typing import Any, Dict, Optional, Union

from globus_sdk import client
from globus_sdk.scopes import GroupsScopes

from .data import BatchMembershipActions, GroupPolicies
from .errors import GroupsAPIError


class GroupsClient(client.BaseClient):
    """
    Client for the
    `Globus Groups API <https://docs.globus.org/api/groups/>`_.

    This provides a relatively low level client to public groups API endpoints.
    You may also consider looking at the GroupsManager as a simpler interface
    to more common actions.

    .. automethodlist:: globus_sdk.GroupsClient
    """

    base_path = "/v2/"
    error_class = GroupsAPIError
    service_name = "groups"
    scopes = GroupsScopes

    def get_my_groups(self, query_params: Optional[Dict[str, Any]] = None):
        """
        Return a list of groups your identity belongs to.

        **External Documentation**

        See
        `Retrieve your groups and membership \
        <https://groups.api.globus.org/redoc#operation/get_my_groups_and_memberships_v2_groups_my_groups_get>`_
        in the API documentation for details.
        """
        return self.get("/groups/my_groups", query_params=query_params)

    def get_group(self, group_id: str, query_params: Optional[Dict[str, Any]] = None):
        """
        Get details about a specific group

        **External Documentation**

        See
        `Get Group \
        <https://groups.api.globus.org/redoc#operation/get_group_v2_groups__group_id__get>`_
        in the API documentation for details.
        """
        return self.get(f"/groups/{group_id}", query_params=query_params)

    def delete_group(
        self, group_id: str, query_params: Optional[Dict[str, Any]] = None
    ):
        """
        Delete a group.

        **External Documentation**

        See
        `Delete a group \
        <https://groups.api.globus.org/redoc#operation/delete_group_v2_groups__group_id__delete>`_
        in the API documentation for details.
        """
        return self.delete(f"/groups/{group_id}", query_params=query_params)

    def create_group(
        self, data: Dict[str, Any], query_params: Optional[Dict[str, Any]] = None
    ):
        """
        Create a group.

        **External Documentation**

        See
        `Create a new group \
        <https://groups.api.globus.org/redoc#operation/create_group_v2_groups_post>`_
        in the API documentation for details.
        """
        return self.post("/groups", data=data, query_params=query_params)

    def get_group_policies(
        self, group_id: str, query_params: Optional[Dict[str, Any]] = None
    ):
        """
        Get policies for the given group

        **External Documentation**

        See
        `Get the policies for the group. \
        <https://groups.api.globus.org/redoc#operation/get_policies_v2_groups__group_id__policies_get>`_
        in the API documentation for details.
        """
        return self.get(f"/groups/{group_id}/policies", query_params=query_params)

    def set_group_policies(
        self,
        group_id: str,
        data: Union[Dict[str, Any], GroupPolicies],
        query_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Set policies for the group.

        **External Documentation**

        See
        `Set the policies for the group. \
        <https://groups.api.globus.org/redoc#operation/update_policies_v2_groups__group_id__policies_put>`_
        in the API documentation for details.
        """
        return self.put(
            f"/groups/{group_id}/policies", data=data, query_params=query_params
        )

    def get_identity_preferences(self, query_params: Optional[Dict[str, Any]] = None):
        """
        Get identity preferences.  Currently this only includes whether the
        user allows themselves to be added to groups.

        **External Documentation**

        See
        `Get the preferences for your identity set. \
        <https://groups.api.globus.org/redoc#operation/get_identity_set_preferences_v2_preferences_get>`_
        in the API documentation for details.
        """
        return self.get("/preferences", query_params=query_params)

    def set_identity_preferences(
        self,
        data: Dict[str, Any],
        query_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Set identity preferences.  Currently this only includes whether the
        user allows themselves to be added to groups.

        **External Documentation**

        See
        `Set the preferences for your identity set. \
        <https://groups.api.globus.org/redoc#operation/put_identity_set_preferences_v2_preferences_put>`_
        in the API documentation for details.
        """
        return self.put("/preferences", data=data, query_params=query_params)

    def get_membership_fields(
        self,
        group_id: str,
        query_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Get membership fields for your identities.

        **External Documentation**

        See
        `Get the membership fields for your identity set. \
        <https://groups.api.globus.org/redoc#operation/get_membership_fields_v2_groups__group_id__membership_fields_get>`_
        in the API documentation for details.
        """
        return self.get(
            f"/groups/{group_id}/membership_fields", query_params=query_params
        )

    def set_membership_fields(
        self,
        group_id: str,
        data: Dict[Any, str],
        query_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Get membership fields for your identities.

        **External Documentation**

        See
        `Set the membership fields for your identity set. \
        <https://groups.api.globus.org/redoc#operation/put_membership_fields_v2_groups__group_id__membership_fields_put>`_
        in the API documentation for details.
        """
        return self.put(
            f"/groups/{group_id}/membership_fields",
            data=data,
            query_params=query_params,
        )

    def batch_membership_action(
        self,
        group_id,
        actions: Union[Dict[str, Any], BatchMembershipActions],
        query_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Execute a batch of actions against several group memberships.

        **External Documentation**

        See
        `Perform actions on members of the group. \
        <https://groups.api.globus.org/redoc#operation/group_membership_post_actions_v2_groups__group_id__post>`_
        in the API documentation for details.
        """
        return self.post(f"/groups/{group_id}", data=actions, query_params=query_params)
