import typing as t

import globus_sdk

specific_flow_client = globus_sdk.SpecificFlowClient("foo")

# running a flow without a notification policy is allowed by the types
specific_flow_client.run_flow({})

# passing a dict[str, t.Any] is allowed (even though the type cannot guarantee safety)
policy_dict: dict[str, t.Any] = {"status": ["INACTIVE"]}
specific_flow_client.run_flow({}, activity_notification_policy=policy_dict)

# passing the object representation is allowed as well
policy_object = globus_sdk.RunActivityNotificationPolicy(status=["FAILED"])
specific_flow_client.run_flow({}, activity_notification_policy=policy_object)

# the object representation does not allow bad values in the status field
globus_sdk.RunActivityNotificationPolicy(status=["FAILURE"])  # type: ignore[list-item]

# passing something of the wrong type (e.g. the status list) is also not allowed
specific_flow_client.run_flow(
    {}, activity_notification_policy=["SUCCEEDED"]  # type: ignore[arg-type]
)
