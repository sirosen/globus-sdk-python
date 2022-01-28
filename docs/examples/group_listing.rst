.. _example_group_listing:

Group Listing Script
--------------------

This example script provides a CSV-formatted listing of the current user's
groups.

It uses the tutorial client ID from the :ref:`tutorial <tutorial>`.
For simplicity, the script will prompt for login on each use.

.. code-block:: python

    import globus_sdk
    from globus_sdk.scopes import GroupsScopes

    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

    auth_client.oauth2_start_flow(
        requested_scopes=GroupsScopes.view_my_groups_and_memberships
    )
    authorize_url = auth_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")

    auth_code = input("Please enter the code here: ").strip()
    tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)
    groups_tokens = tokens.by_resource_server["groups.api.globus.org"]

    # construct an AccessTokenAuthorizer and use it to construct the
    # TransferClient
    groups_client = globus_sdk.GroupsClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(groups_tokens["access_token"])
    )

    # print out in CSV format
    # note that 'name' could have a comma in it, so this is slightly unsafe
    print("ID,Name,Type,Session Enforcement,Roles")
    for group in groups_client.get_my_groups():
        # parse the group to get data for output
        if group.get("enforce_session"):
            session_enforcement = "strict"
        else:
            session_enforcement = "not strict"
        roles = ",".join({m["role"] for m in group["my_memberships"]})

        print(
            ",".join(
                [
                    group["id"],
                    group["name"],
                    group["group_type"],
                    session_enforcement,
                    roles,
                ]
            )
        )
