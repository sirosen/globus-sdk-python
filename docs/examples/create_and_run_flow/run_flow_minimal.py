#!/usr/bin/env python

import argparse
import os
import sys
import time

import globus_sdk
from globus_sdk.tokenstorage import SimpleJSONFileAdapter

MY_FILE_ADAPTER = SimpleJSONFileAdapter(os.path.expanduser("~/.sdk-manage-flow.json"))

# tutorial client ID
# we recommend replacing this with your own client for any production use-cases
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

NATIVE_CLIENT = globus_sdk.NativeAppAuthClient(CLIENT_ID)


def do_login_flow(scope):
    NATIVE_CLIENT.oauth2_start_flow(requested_scopes=scope)
    authorize_url = NATIVE_CLIENT.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")
    auth_code = input("Please enter the code here: ").strip()
    tokens = NATIVE_CLIENT.oauth2_exchange_code_for_tokens(auth_code)
    return tokens


def get_tokens(flow_id, force=False):
    scopes = globus_sdk.SpecificFlowClient(flow_id).scopes

    # try to load the tokens from the file, possibly returning None
    if MY_FILE_ADAPTER.file_exists():
        tokens = MY_FILE_ADAPTER.get_token_data(flow_id)
    else:
        tokens = None

    if tokens is None or force:
        # do a login flow, getting back initial tokens
        response = do_login_flow(scopes.user)
        # now store the tokens and pull out the correct token
        MY_FILE_ADAPTER.store(response)
        tokens = response.by_resource_server[flow_id]

    # allow for 60 seconds of potential clock skew or delay
    # if the call was not "force=True", potentially re-enter
    leeway = 60
    if not force and (time.time() > tokens["expires_at_seconds"] - leeway):
        tokens = get_tokens(flow_id, force=True)

    return tokens


def get_flow_client(flow_id):
    tokens = get_tokens(flow_id)
    return globus_sdk.SpecificFlowClient(
        flow_id, authorizer=globus_sdk.AccessTokenAuthorizer(tokens["access_token"])
    )


def run_flow(args):
    flow_client = get_flow_client(args.FLOW_ID)
    print(flow_client.run_flow({}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("FLOW_ID", help="Flow ID for delete")
    args = parser.parse_args()

    try:
        run_flow(args)
    except globus_sdk.FlowsAPIError as e:
        print(f"API Error: {e.code} {e.message}")
        print(e.text)
        sys.exit(1)


if __name__ == "__main__":
    main()
