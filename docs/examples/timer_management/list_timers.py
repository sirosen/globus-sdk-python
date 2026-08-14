import globus_sdk

# Tutorial Client ID - <replace this with your own client>
NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"


def main():
    with globus_sdk.UserApp("manage-timers-example", client_id=NATIVE_CLIENT_ID) as app:
        with globus_sdk.TimersClient(app=app) as client:
            list_timers(client)


def list_timers(client: globus_sdk.TimersClient) -> None:
    first = True
    for record in client.list_jobs(query_params={"filter_active": True})["jobs"]:
        if not first:
            print("---")
        first = False
        print("name:", record["name"])
        print("id:", record["job_id"])


if __name__ == "__main__":
    main()
