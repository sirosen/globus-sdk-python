from enum import Enum
from typing import Sequence

from globus_sdk import utils


class GroupRole(Enum):
    member = "member"
    manager = "manager"
    admin = "admin"


class GroupMemberVisibility(Enum):
    members = "members"
    managers = "managers"


class GroupVisibility(Enum):
    authenticated = "authenticated"
    private = "private"


class GroupRequiredSignupFields(Enum):
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

    .. automethodlist:: globus_sdk.BatchMembershipActions
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

    def add_members(
        self, identity_ids: Sequence[str], role: GroupRole = GroupRole.member
    ):
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

    def invite_members(
        self, identity_ids: Sequence[str], role: GroupRole = GroupRole.member
    ):
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
