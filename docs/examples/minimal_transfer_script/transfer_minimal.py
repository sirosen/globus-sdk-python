import globus_sdk

# tutorial client ID (we recommend replacing this with your own client)
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

# Replace these with your own collection UUIDs
SOURCE_COLLECTION_ID = "..."
DEST_COLLECTION_ID = "..."

# create a Transfer task consisting of one or more items
task_data = globus_sdk.TransferData(SOURCE_COLLECTION_ID, DEST_COLLECTION_ID)
task_data.add_item(
    "/share/godata/file1.txt",  # source
    "/~/minimal-example-transfer-script-destination.txt",  # dest
)

# create an app to manage login, use it to create a client, and submit,
# getting back the task ID
with globus_sdk.UserApp(
    "minimal-transfer-example",
    client_id=CLIENT_ID,
    # we set the 'auto_redrive_gares' flag, which enables handling for missing
    # auth requirements when the script is run against a changing set of collection IDs
    config=globus_sdk.GlobusAppConfig(auto_redrive_gares=True),
) as app:
    with globus_sdk.TransferClient(app=app) as transfer_client:
        task_doc = transfer_client.submit_transfer(task_data)

task_id = task_doc["task_id"]
print(f"submitted transfer, task_id={task_id}")
