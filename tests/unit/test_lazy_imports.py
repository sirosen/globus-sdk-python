import pytest

import globus_sdk


def test_explicit_dir_func_works():
    assert "TransferClient" in dir(globus_sdk)
    assert "__all__" in dir(globus_sdk)


@pytest.mark.filterwarnings("ignore::globus_sdk.RemovedInV4Warning")
def test_force_eager_imports_can_run():
    # this check will not do much, other than ensuring that this does not crash
    globus_sdk._force_eager_imports()


def test_attribute_error_on_bad_name():
    with pytest.raises(AttributeError) as excinfo:
        globus_sdk.DEIMOS_DOWN_REMOVE_ALL_PLANTS

    err = excinfo.value
    assert (
        str(err) == "module globus_sdk has no attribute DEIMOS_DOWN_REMOVE_ALL_PLANTS"
    )
