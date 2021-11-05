def test_transfer_task_list(run_reveal_type):
    # task_list is decorated with documentation and pagination helpers; make sure that
    # the typing information is preserved
    got_type = run_reveal_type("globus_sdk.TransferClient.task_list")
    assert got_type != "def (*Any, **Any) -> Any"
    # don't check the full type: just make sure it starts with a properly annotated
    # self-type if this is present, it means that the type information was preserved
    assert got_type.startswith(
        "def (self: globus_sdk.services.transfer.client.TransferClient"
    )
