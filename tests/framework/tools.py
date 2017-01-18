import os


def get_fixture_file_dir():
    return os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            '../files'
        )
    )
