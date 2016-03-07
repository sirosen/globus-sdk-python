"""
Load config files once per interpreter invocation.
"""

import os.path
from ConfigParser import SafeConfigParser


_parser = None


def get_service_url(environment, service):
    section = "environment " + environment
    option = service + "_service"
    # TODO: validate with urlparse?
    return _get(section, option)


def _get(section, option):
    global _parser
    if _parser is None:
        _parser = _load_config()
    return _parser.get(section, option)


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
