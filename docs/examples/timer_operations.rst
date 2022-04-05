Timer Operations Script
-----------------------

This example demonstrates the usage of methods on the Timer client. Note that we first
need a Transfer client set up in order to create the ``TransferData`` we will use to
define our recurring Timer job.

.. code-block:: python

    import os
    from datetime import datetime, timedelta

    from globus_sdk import (
        AccessTokenAuthorizer,
        NativeAppAuthClient,
        TimerClient,
        TimerJob,
        TransferClient,
        TransferData,
    )

    GOEP1 = "ddb59aef-6d04-11e5-ba46-22000b92c6ec"
    GOEP2 = "ddb59af0-6d04-11e5-ba46-22000b92c6ec"
    TIMER_CLIENT_ID = "524230d7-ea86-4a52-8312-86065a9e0417"
    TIMER_SCOPE = f"https://auth.globus.org/scopes/{TIMER_CLIENT_ID}/timer"
    TRANSFER_SCOPE = "urn:globus:auth:scope:transfer.api.globus.org:all"
    SCOPES = [TIMER_SCOPE, TRANSFER_SCOPE]

    # Get access tokens to use for both Transfer and Timer
    native_client.oauth2_start_flow(requested_scopes=SCOPES)
    authorize_url = native_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")
    auth_code = input("Enter the auth code here: ").strip()
    token_response = native_client.oauth2_exchange_code_for_tokens(auth_code)
    timer_token = token_response.by_resource_server[TIMER_CLIENT_ID]["access_token"]
    transfer_token = token_response.by_resource_server["transfer.api.globus.org"]["access_token"]

    # Set up a transfer client and create a `TransferData` object
    transfer_authorizer = AccessTokenAuthorizer(transfer_token)
    transfer_client = TransferClient(authorizer=transfer_authorizer)
    data = TransferData(transfer_client, GOEP1, GOEP2)
    data.add_item("/share/godata/file1.txt", "/~/file1.txt")

    # Set up the Timer client
    timer_authorizer = AccessTokenAuthorizer(timer_token)
    timer_client = TimerClient(authorizer=timer_authorizer)

    # Create a Timer job, set to run the above transfer 2 times
    start = datetime.utcnow()
    interval = timedelta(minutes=30)
    name = "sdk-timer-example"
    job = TimerJob.from_transfer_data(data, start, interval, stop_after_n=2, name=name)
    response = timer_client.create_job(job)
    assert response.http_status == 201
    job_id = response["job_id"]
    print(f"Timer job ID: {job_id}")

    all_jobs = timer_client.list_jobs()
    assert job_id in {job["job_id"] for job in timer_client.list_jobs()["jobs"]}

    get_job_response = timer_client.get_job(job_id)
    assert get_job_response.http_status == 200
    assert get_job_response["name"] == name

    # Later, you could run this function to clean up the job:
    def delete_timer_job(job_id):
        delete_job_response = timer_client.delete_job(job_id)
        assert delete_job_response.http_status == 200
