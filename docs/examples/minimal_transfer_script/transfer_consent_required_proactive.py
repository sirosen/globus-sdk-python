import argparse

import globus_sdk
from globus_sdk.scopes import TransferScopes

# do basic argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("SRC")
parser.add_argument("DST")
args = parser.parse_args()

# tutorial client ID (we recommend replacing this with your own client)
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
APP_NAME = "proactive-transfer-consent-example"


# Try an ls on the source and destination to see if ConsentRequired errors are raised --
# if they are, a fresh login flow will *not* be triggered.
#
# This is more sophisticated than handling with `redrive_gares=True` and makes
# sure that the user is only prompted to login *one* extra time, even if both
# collections require additional consent.
def probe_for_consent_required(
    transfer_client: globus_sdk.TransferClient, targets: list[str]
) -> list[str]:
    consent_required_scopes: list[str] = []

    for target in targets:
        try:
            transfer_client.operation_ls(target, path="/")
        # catch all errors and discard those other than ConsentRequired
        # e.g. ignore PermissionDenied errors as not relevant
        except globus_sdk.TransferAPIError as err:
            if err.info.consent_required:
                consent_required_scopes.extend(
                    err.info.consent_required.required_scopes
                )

    return consent_required_scopes


with globus_sdk.UserApp(APP_NAME, client_id=CLIENT_ID) as app:
    with globus_sdk.TransferClient(app=app) as transfer_client:
        consent_required_scopes = probe_for_consent_required(
            transfer_client, [args.SRC, args.DST]
        )

# the block above may or may not populate this list
# but if it does, handle ConsentRequired with a new login
if consent_required_scopes:
    print(
        "One of your endpoints requires consent in order to be used.\n"
        "You must login a second time to grant consents.\n\n"
    )
    with globus_sdk.UserApp(
        APP_NAME,
        client_id=CLIENT_ID,
        scope_requirements={
            TransferScopes.resource_server: consent_required_scopes
            + [TransferScopes.all]
        },
    ) as app:
        app.login()


# From this point onwards, the example is exactly the same as the previous scripts.
# We will *not* set `redrive_gares=True`, on the grounds that if you want to use this
# in a context like a job submission system, a prompt for login is not helpful if the
# consent was revoked or insufficient.

task_data = globus_sdk.TransferData(
    source_endpoint=args.SRC, destination_endpoint=args.DST
)
task_data.add_item(
    "/share/godata/file1.txt",  # source
    "/~/example-transfer-script-destination.txt",  # dest
)

with globus_sdk.UserApp(APP_NAME, client_id=CLIENT_ID) as app:
    with globus_sdk.TransferClient(app=app) as transfer_client:
        task_doc = transfer_client.submit_transfer(task_data)

task_id = task_doc["task_id"]
print(f"submitted transfer, task_id={task_id}")
