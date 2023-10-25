from globus_sdk import GroupPolicies


def test_group_policies_can_explicitly_null_ha_timeout():
    # step 1: confirm that the auth assurance timeout is not in the baseline
    #         doc which does not specify it
    kwargs = {
        "is_high_assurance": True,
        "group_visibility": "private",
        "group_members_visibility": "members",
        "join_requests": False,
        "signup_fields": [],
    }
    baseline = GroupPolicies(**kwargs)
    assert isinstance(baseline, GroupPolicies)
    assert "authentication_assurance_timeout" not in baseline

    # step 2: confirm that the auth assurance timeout is in the doc when
    #         set to an integer value, even 0
    kwargs["authentication_assurance_timeout"] = 0
    with_falsy_timeout = GroupPolicies(**kwargs)
    assert with_falsy_timeout["authentication_assurance_timeout"] == 0

    # step 3: confirm that the auth assurance timeout is in the doc when
    #         set to None
    kwargs["authentication_assurance_timeout"] = None
    with_null_timeout = GroupPolicies(**kwargs)
    assert with_null_timeout["authentication_assurance_timeout"] is None
