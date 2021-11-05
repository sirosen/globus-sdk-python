def test_resource_server_classproperty(run_reveal_type):
    got_type = run_reveal_type("globus_sdk.BaseClient.resource_server")
    assert got_type == "Union[builtins.str, None]"


def test_resource_server_classproperty_on_instance(run_reveal_type):
    got_type = run_reveal_type("globus_sdk.BaseClient().resource_server")
    assert got_type == "Union[builtins.str, None]"
