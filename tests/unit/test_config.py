import globus_sdk
from six.moves.configparser import ConfigParser


def test_get_lib_config_path():
    """Test lib config file exists, is minimally well formed"""
    path = globus_sdk.config._get_lib_config_path()

    # name is "about right"
    file_name = "globus.cfg"
    assert path.endswith(file_name)

    # ensure that it parses using configparser
    parser = ConfigParser()
    parser.read(path)
    # and check that 'default' and 'preview' are populated
    for env in ('default', 'preview'):
        section = 'environment {}'.format(env)
        for key in ('auth_service', 'nexus_service', 'transfer_service',
                    'search_service'):
            opt = parser.get(section, key)
            assert opt
