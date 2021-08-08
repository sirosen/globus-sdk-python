from enum import Enum
from typing import Optional, Sequence

from globus_sdk import client, utils
from globus_sdk.scopes import GroupsScopes

from .errors import GroupsAPIError


class Role(Enum):

    member = "member"
    manager = "manager"
    admin = "admin"


class GroupMemberVisibility(Enum):

    members = "members"
    managers = "managers"


class GroupVisibility(Enum):

    authenticated = "authenticated"
    private = "private"


class RequiredSignupFields(Enum):
    institution = "institution"
    current_project_name = "current_project_name"
    address = "address"
    city = "city"
    state = "state"
    country = "country"
    address1 = "address1"
    address2 = "address2"
    zip = "zip"
    phone = "phone"
    department = "department"
    field_of_science = "field_of_science"


class BatchMembershipActions(utils.PayloadWrapper):
    """
    An object used to represent a batch action on memberships of a group.
    `Perform actions on group members
    <https://groups.api.globus.org/redoc#operation/group_membership_post_actions_v2_groups__group_id__post>`_.

    .. automethodlist:: globus_sdk.GroupsClient
    """

    def accept_invites(self, identity_ids: Sequence[str]):
        """
        Accept invites for identities.  The identities must belong to
        the identity set of authenticated user.
        """
        self.setdefault("accept", []).extend(
            {"identity_id": identity_id} for identity_id in identity_ids
        )
        return self

    def add_members(self, identity_ids: Sequence[str], role: Role = Role.member):
        """
        Add a list of identities to a group with the given role.
        """
        self.setdefault("add", []).extend(
            {"identity_id": identity_id, "role": role.value}
            for identity_id in identity_ids
        )
        return self

    def approve_pending(self, identity_ids: Sequence[str]):
        """
        Approve a list of identities with pending join requests.
        """
        self.setdefault("approve", []).extend(
            {"identity_id": identity_id} for identity_id in identity_ids
        )
        return self

    def decline_invites(self, identity_ids: Sequence[str]):
        """
        Decline an invitation for a given set of identities.
        """
        self.setdefault("decline", []).extend(
            {"identity_id": identity_id} for identity_id in identity_ids
        )
        return self

    def invite_members(self, identity_ids: Sequence[str], role: Role = Role.member):
        """
        Invite a list of identities to a group with the given role.
        """
        self.setdefault("invite", []).extend(
            {"identity_id": identity_id, "role": role.value}
            for identity_id in identity_ids
        )
        return self

    def join(self, identity_ids: Sequence[str]):
        """
        Join a group with the given identities.  The identities must be in the
        authenticated users identity set.
        """
        self.setdefault("join", []).extend(
            {"identity_id": identity_id} for identity_id in identity_ids
        )
        return self

    def leave(self, identity_ids: Sequence[str]):
        """
        Leave a group that one of the identities in the authenticated user's
        identity set is a member of.
        """
        self.setdefault("leave", []).extend(
            {"identity_id": identity_id} for identity_id in identity_ids
        )
        return self

    def reject_join_requests(self, identity_ids: Sequence[str]):
        """
        Reject a members that have requested to join the group.
        """
        self.setdefault("reject", []).extend(
            {"identity_id": identity_id} for identity_id in identity_ids
        )
        return self

    def remove_members(self, identity_ids: Sequence[str]):
        """
        Remove members from a group.  This must be done as an admin or manager
        of the group.
        """
        self.setdefault("remove", []).extend(
            {"identity_id": identity_id} for identity_id in identity_ids
        )
        return self

    def request_join(self, identity_ids: Sequence[str]):
        """
        Request to join a group.
        """
        self.setdefault("request_join", []).extend(
            {"identity_id": identity_id} for identity_id in identity_ids
        )
        return self



class GroupsClient(client.BaseClient):
    """
    Client for the
    `Globus Groups API <https://docs.globus.org/api/groups/>`_.

    .. automethodlist:: globus_sdk.GroupsClient
    """

    base_path = "/v2/"
    error_class = GroupsAPIError
    service_name = "groups"
    scopes = GroupsScopes

    def get_my_groups(self, **query_params):
        """
        Return a list of groups your identity belongs to.
        """
        return self.get("/groups/my_groups", query_params=query_params)

    def get_group(self, group_id: str, **query_params):
        """
        Get details about a specific group
        """
        return self.get(f"/groups/{group_id}", query_params=query_params)

    def delete_group(self, group_id: str):
        return self.delete(f"/groups/{group_id}")

    def create_group(self, name: str, parent_id: Optional[str] = None):
        """
        Create a group with the given name.  If a parent id is included, the
        group will be a subgroup of the given parent group.
        """
        data = {"name": name, "parent_id": parent_id}
        return self.post("/groups", data=data)

    def get_group_policies(self, group_id: str):
        """
        Get policies for the given group
        """
        return self.get(f"/groups/{group_id}/policies")

    def set_group_policies(
        self,
        group_id: str,
        is_high_assurance: bool,
        group_visibility: GroupVisibility,
        group_members_visibility: GroupMemberVisibility,
        join_requests: bool,
        signup_fields: Sequence[RequiredSignupFields],
        authentication_assurance_timeout: Optional[int] = None,
    ):
        data = {
            "is_high_assurance": is_high_assurance,
            "group_visibility": group_visibility.value,
            "group_members_visibility": str(group_members_visibility),
            "join_requests": join_requests,
            "signup_fields": [field.value for field in signup_fields],
        }
        if authentication_assurance_timeout:
            data["authentication_assurance_timeout"] = authentication_assurance_timeout

        return self.put(f"/groups/{group_id}/policies", data=data)

    def get_identity_preferences(self):
        """
        Get identity preferences.  Currently this only includes whether the
        user allows themselves to be added to groups.
        """
        return self.get("/preferences")

    def set_identity_preferences(self, preferences: dict):
        """
        Set identity preferences.  Currently this only includes whether the
        user allows themselves to be added to groups.
        """
        return self.put("/preferences", data=preferences)

    def get_membership_fields(self, group_id: str):
        return self.get(f"/groups/{group_id}/membership_fields")

    def set_membership_fields(self, group_id: str, membership_fields: dict):
        return self.put(f"/groups/{group_id}/membership_fields", data=membership_fields)

    def batch_membership_action(self, group_id, actions: BatchMembershipActions):
        """
        Execute a batch of actions against several group memberships.
        """
        return self.post(f"/groups/{group_id}", data=actions)

    def accept_invite(self, group_id: str, identity_id: str):
        """
        Accept invite for an identity.  The identity must belong to
        the identity set of the authenticated user.
        """
        actions = BatchMembershipActions().accept_invites([identity_id])
        return self.batch_membership_action(group_id, actions)

    def add_member(self, group_id: str, identity_id: str, role: Role = Role.member):
        """
        Add a list of identities to a group with the given role.
        """
        actions = BatchMembershipActions().add_members([identity_id], role)
        return self.batch_membership_action(group_id, actions)

    def approve_pending(self, group_id: str, identity_id: str):
        """
        Approve a list of identities with pending join requests.
        """
        actions = BatchMembershipActions().approve_pending([identity_id])
        return self.batch_membership_action(group_id, actions)

    def decline_invite(self, group_id: str, identity_id: str):
        """
        Decline an invitation for a given identity.
        """
        actions = BatchMembershipActions().decline_invites([identity_id])
        return self.batch_membership_action(group_id, actions)

    def invite_member(self, group_id: str, identity_id: str, role: Role = Role.member):
        """
        Invite an identity to a group with the given role.
        """
        actions = BatchMembershipActions().invite_members([identity_id], role)
        return self.batch_membership_action(group_id, actions)

    def join(self, group_id: str, identity_id: str):
        """
        Join a group with the given identity.  The identity must be in the
        authenticated users identity set.
        """
        actions = BatchMembershipActions().join([identity_id])
        return self.batch_membership_action(group_id, actions)

    def leave(self, group_id: str, identity_id: str):
        """
        Leave a group that one of the identities in the authenticated user's
        identity set is a member of.
        """
        actions = BatchMembershipActions().leave([identity_id])
        return self.batch_membership_action(group_id, actions)

    def reject_join_request(self, group_id: str, identity_id: str):
        """
        Reject a member that has requested to join the group.
        """
        actions = BatchMembershipActions().reject_join_requests([identity_id])
        return self.batch_membership_action(group_id, actions)

    def remove_member(self, group_id: str, identity_id: str):
        """
        Remove members from a group.  This must be done as an admin or manager
        of the group.
        """
        actions = BatchMembershipActions().remove_members([identity_id])
        return self.batch_membership_action(group_id, actions)

    def request_join(self, group_id: str, identity_id: str):
        """
        Request to join a group.
        """
        actions = BatchMembershipActions().request_join([identity_id])
        return self.batch_membership_action(group_id, actions)
