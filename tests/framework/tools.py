import os
import json
import time
from functools import wraps

from globus_sdk.exc import NetworkError


def get_fixture_file_dir():
    return os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            "../files"
        )
    )


def get_client_data():
    dirname = get_fixture_file_dir()
    ret = {}
    for fname in ("native_app_client1", "confidential_app_client1",
                  "resource_server_client"):
        with open(os.path.join(dirname,
                               "auth_fixtures",
                               fname + ".json")) as f:
            ret[fname] = json.load(f)
    return ret


def get_user_data():
    dirname = get_fixture_file_dir()
    ret = {}
    for uname in ("sdktester1a", "sdktester2b", "go"):
        with open(os.path.join(dirname,
                               "auth_fixtures",
                               uname + "@globusid.org.json")) as f:
            ret[uname] = json.load(f)
    return ret


def retry_errors(retries=2, error_classes=(NetworkError,)):
    """
    A decorator which wraps tests to make them retry x times after a short
    sleep (with exponential backoff) when a class of errors occurs.

    Typically good for making tests robust to NetworkErrors

    retries is the number of times to retry
    error_classes is a tuple of classes of errors to retry
    """
    def inner_decorator(f):
        @wraps(f)
        def result_func(*args, **kwargs):
            last_error = None
            sleep_time = 1
            count = 0
            while count <= retries:
                try:
                    return f(*args, **kwargs)
                except error_classes as e:
                    last_error = e
                    time.sleep(sleep_time)
                    sleep_time *= 2
                    count += 1
            assert last_error is not None
            raise last_error

        return result_func

    return inner_decorator
