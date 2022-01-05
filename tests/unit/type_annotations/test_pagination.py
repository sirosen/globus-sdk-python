import re


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


def test_typed_paginated_transfer_task_list(run_reveal_type):
    # the typed_paginator variant of a method should preserve the parameters
    # (ParamSpec) but have an altered return type
    got_type = run_reveal_type(
        "tc.typed_paginator(tc.task_list)",
        preamble="""\
import globus_sdk

tc = globus_sdk.TransferClient()
""",
    )

    # this is what we'd see if type information were discarded for any reason...
    assert got_type != "def (*Any, **Any) -> Any"

    # the start of the parameters for task_list is `*` (no positionals)
    assert got_type.startswith("def (*, ")
    # the result type ("right hand side") is a paginator of iterable responses
    rhs = got_type.split("->")[-1].strip()
    assert re.search(r"Paginator\[globus_sdk\.([^.]+\.)*IterableTransferResponse", rhs)
