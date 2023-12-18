from __future__ import annotations

import json

import pytest

from globus_sdk import exc
from globus_sdk._testing import get_last_request, load_response


@pytest.mark.parametrize(
    "case_name",
    (
        "project_id_str",
        "project_id_uuid",
        "high_assurance",
        "not_high_assurance",
        "authentication_assurance_timeout",
        "display_name",
        "description",
        "domain_constraints_include",
        "empty_domain_constraints_include",
        "no_domain_constraints_include",
        "domain_constraints_exclude",
        "empty_domain_constraints_exclude",
        "no_domain_constraints_exclude",
    ),
)
def test_create_policy(
    service_client,
    case_name: str,
):
    meta = load_response(service_client.create_policy, case=case_name).metadata

    res = service_client.create_policy(**meta["args"])
    for k, v in meta["response"].items():
        assert res["policy"][k] == v


def test_compatible_create_policy_usage_rejects_too_many_positionals(service_client):
    load_response(service_client.create_policy)
    with pytest.raises(
        TypeError,
        match=r"create_policy\(\) takes 5 positional arguments but 6 were given",
    ):
        service_client.create_policy(1, 2, 3, 4, 5, 6)


@pytest.mark.parametrize(
    "posargs, keyword_args, expect_data",
    [
        pytest.param(
            ["my_project_id"],
            {
                "display_name": "my_display_name",
                "description": "my_description",
            },
            {
                "project_id": "my_project_id",
                "display_name": "my_display_name",
                "description": "my_description",
            },
            id="one_arg",
        ),
        pytest.param(
            [
                "my_project_id",
                True,
            ],
            {
                "display_name": "my_display_name",
                "description": "my_description",
            },
            {
                "project_id": "my_project_id",
                "high_assurance": True,
                "display_name": "my_display_name",
                "description": "my_description",
            },
            id="two_arg",
        ),
        pytest.param(
            [
                "my_project_id",
                True,
                101,
            ],
            {
                "display_name": "my_display_name",
                "description": "my_description",
            },
            {
                "project_id": "my_project_id",
                "high_assurance": True,
                "authentication_assurance_timeout": 101,
                "display_name": "my_display_name",
                "description": "my_description",
            },
            id="three_arg",
        ),
        pytest.param(
            [
                "my_project_id",
                True,
                101,
                "my_display_name",
            ],
            {
                "description": "my_description",
            },
            {
                "project_id": "my_project_id",
                "high_assurance": True,
                "authentication_assurance_timeout": 101,
                "display_name": "my_display_name",
                "description": "my_description",
            },
            id="four_arg",
        ),
        pytest.param(
            [
                "my_project_id",
                True,
                101,
                "my_display_name",
                "my_description",
            ],
            {},
            {
                "project_id": "my_project_id",
                "high_assurance": True,
                "authentication_assurance_timeout": 101,
                "display_name": "my_display_name",
                "description": "my_description",
            },
            id="five_arg",
        ),
    ],
)
def test_valid_compatible_policy_usage_emits_warning(
    service_client, posargs, keyword_args, expect_data
):
    load_response(service_client.create_policy)
    with pytest.warns(
        exc.RemovedInV4Warning,
        match=r"'AuthClient\.create_policy' received positional arguments",
    ):
        service_client.create_policy(*posargs, **keyword_args)

    lastreq = get_last_request()
    sent_data = json.loads(lastreq.body)
    assert sent_data["policy"] == expect_data


@pytest.mark.parametrize(
    "posargs, keyword_args, missing_arg_count, missing_arg_strlist",
    [
        pytest.param(
            [],
            {"project_id": "my_project_id", "description": "my_description"},
            1,
            "'display_name'",
            id="missing_display_name",
        ),
        pytest.param(
            ["my_project_id"],
            {"description": "my_description"},
            1,
            "'display_name'",
            id="missing_display_name_with_posarg",
        ),
        pytest.param(
            [],
            {"project_id": "my_project_id"},
            2,
            "'display_name' and 'description'",
            id="missing_display_name_and_description",
        ),
        pytest.param(
            ["my_project_id"],
            {},
            2,
            "'display_name' and 'description'",
            id="missing_display_name_and_description_with_posarg",
        ),
        pytest.param(
            [],
            {},
            3,
            "'project_id', 'display_name', and 'description'",
            id="no_args",
        ),
    ],
)
def test_policy_usage_warns_and_errors_when_required_args_are_missing(
    service_client, posargs, keyword_args, missing_arg_count, missing_arg_strlist
):
    with pytest.raises(
        TypeError,
        match=(
            f"missing {missing_arg_count} "
            f"required keyword-only arguments?: {missing_arg_strlist}"
        ),
    ):
        # warning is emitted if posargs is nonempty
        if posargs:
            with pytest.warns(
                exc.RemovedInV4Warning,
                match="'AuthClient.create_policy()' received positional arguments",
            ):
                service_client.create_policy(*posargs, **keyword_args)
        else:
            service_client.create_policy(*posargs, **keyword_args)


@pytest.mark.parametrize(
    "posargs, keyword_args",
    (
        (["my_project_id"], {"project_id": "my_project_id2"}),
        (["my_project_id", False], {"high_assurance": True}),
        (["my_project_id", False, 101], {"authentication_assurance_timeout": 102}),
        (["my_project_id", False, 101, "foo"], {"display_name": "bar"}),
        (["my_project_id", False, 101, "foo", "my_description"], {"description": "hi"}),
    ),
)
def test_policy_usage_warns_and_errors_when_argument_is_supplied_twice(
    service_client, posargs, keyword_args
):
    assert len(keyword_args) == 1
    argname = next(iter(keyword_args))

    with pytest.raises(
        TypeError,
        match=f"create_policy\\(\\) got multiple values for argument '{argname}'",
    ):
        with pytest.warns(
            exc.RemovedInV4Warning,
            match="'AuthClient.create_policy()' received positional arguments",
        ):
            service_client.create_policy(*posargs, **keyword_args)
