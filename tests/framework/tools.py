import os
import json


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
    for fname in ('native_app_client1', 'confidential_app_client1'):
        with open(os.path.join(dirname,
                               'auth_fixtures',
                               fname + '.json')) as f:
            ret[fname] = json.load(f)
    return ret
