import argparse

import globus_sdk

# Tutorial Client ID - <replace this with your own client>
NATIVE_CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("TIMER_ID")
    args = parser.parse_args()

    with globus_sdk.UserApp("manage-timers-example", client_id=NATIVE_CLIENT_ID) as app:
        with globus_sdk.TimersClient(app=app) as client:
            client.delete_job(args.TIMER_ID)
            print("Finished deleting timer.")


if __name__ == "__main__":
    main()
