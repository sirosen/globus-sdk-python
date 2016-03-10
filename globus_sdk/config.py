"""
Load config files once per interpreter invocation.
"""

import os.path
from ConfigParser import SafeConfigParser, NoOptionError


_parser = None


def get_service_url(environment, service):
    section = _env_section(environment)
    option = service + "_service"
    # TODO: validate with urlparse?
    return _get(section, option)


def get_auth_token(environment):
    """
    Fetch any auth token from the config, if one is present
    """
    section = _env_section(environment)

    tkn = _get(section, 'auth_token', failover_to_general=True)

    return tkn


def _env_section(envname):
    return 'environment ' + envname


def _get(section, option, failover_to_general=False):
    """
    Attempt to lookup an option in the config file. Optionally failover to the
    [general] section if the option is not found.
    Returns None for an unfound key, rather than raising a NoOptionError.
    """
    global _parser
    if _parser is None:
        _parser = _load_config()
    try:
        return _parser.get(section, option)
    except NoOptionError:
        if failover_to_general:
            return _get('general', option)
        return None


def _load_config():
    parser = SafeConfigParser()
    # TODO: /etc is not windows friendly, not sure about expanduser
    parser.read([_get_lib_config_path(), "/etc/globus.cfg",
                 os.path.expanduser("~/.globus.cfg")])
    return parser


def _get_lib_config_path():
    fname = "globus.cfg"
    try:
        import pkg_resources
        path = pkg_resources.resource_filename("globus_sdk", fname)
    except ImportError:
        pkg_path = os.path.dirname(__file__)
        path = os.path.join(pkg_path, fname)
    return path
