import globus_sdk

# this is the tutorial client ID
# replace this string with your ID for production use
CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

# create a client for interactions with Globus Auth
auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

# using that client, do a login flow for Globus Groups credentials
auth_client.oauth2_start_flow(
    requested_scopes=globus_sdk.GroupsClient.scopes.view_my_groups_and_memberships
)
authorize_url = auth_client.oauth2_get_authorize_url()
print(f"Please go to this URL and login:\n\n{authorize_url}\n")

auth_code = input("Please enter the code here: ").strip()
tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)

# extract tokens from the response which match Globus Groups
groups_tokens = tokens.by_resource_server[globus_sdk.GroupsClient.resource_server]

# construct an AccessTokenAuthorizer and use it to construct the GroupsClient
groups_client = globus_sdk.GroupsClient(
    authorizer=globus_sdk.AccessTokenAuthorizer(groups_tokens["access_token"])
)

# print in CSV format
# ('name' could actually have commas in it, so it is quoted)
print("ID,Name,Roles")
for group in groups_client.get_my_groups():
    roles = "|".join({m["role"] for m in group["my_memberships"]})
    print(",".join([group["id"], f'"{group["name"]}"', roles]))
