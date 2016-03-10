"""
Load config files once per interpreter invocation.
"""

import os
from ConfigParser import (
    SafeConfigParser, NoOptionError, MissingSectionHeaderError)

# use StringIO to wrap up reads from file-like objects in new file-like objects
# import it in a py2/py3 safe way
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class GlobusConfigParser(SafeConfigParser):
    """
    A very slightly modified config parser that captures
    MissingSectionHeaderError and injects '[general]\n' at the beginning of
    file contents IFF it is triggered on a filename during a call to read() or
    readfp()
    """
    def _read(self, fp, fpname):
        """
        Wrap the parent class's _read() function, which is what handles
        slurping things in from raw file-like objects.
        This is slightly more dangerous than overriding read() and readfp()
        directly, as a future version of Python could change the implementation
        of _read() significantly, but it's also easier to read and understand.
        Given that we're already going to be subclassing from a stdlib class,
        that danger already exists a bit -- doesn't seem that bad.
        """
        # wrap the file-like object in a StringIO so that we can do quick and
        # easy calls to seek(0) without touching disk or worrying about reading
        # something that doesn't support seek() (like a socket)
        # call me paranoid, but it might save us down the line
        wrapped_fp = StringIO(fp.read())
        try:
            return SafeConfigParser._read(self, wrapped_fp, fpname)
        except MissingSectionHeaderError:
            # go back to the beginning so that we can do a fresh read
            wrapped_fp.seek(0)
            # create a new StringIO with the desired content because write()
            # would just append
            wrapped_fp = StringIO('[general]\n'+wrapped_fp.read())
            # don't capture errors here -- there shouldn't be any
            # MissingSectionHeaderErrors anymore because the section is right
            # at the top
            return SafeConfigParser._read(self, wrapped_fp, fpname)

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

    tkn = _get(section, 'auth_token', failover_to_general=True, check_env=True)

    return tkn


def _env_section(envname):
    return 'environment ' + envname


def _get(section, option, failover_to_general=False, check_env=False):
    """
    Attempt to lookup an option in the config file. Optionally failover to the
    [general] section if the option is not found.

    Also optionally, check for a relevant environment variable, which is named
    always as GLOBUS_SDK_{option.upper()}. Note that 'section' doesn't slot
    into the naming at all. Otherwise, we'd have to contend with
    GLOBUS_SDK_GENERAL_... for almost everything, and
    GLOBUS_SDK_ENVIRONMENT\ PROD_... which is awful.

    Returns None for an unfound key, rather than raising a NoOptionError.
    """
    global _parser
    if _parser is None:
        _parser = _load_config()

    # if this is a config option which checks the environment, look there
    # *first* for a value -- env values have higher precedence than config
    # files so that you can locally override the behavior of a command in a
    # given shell or subshell
    env_option_name = 'GLOBUS_SDK_{}'.format(option.upper())
    if check_env and env_option_name in os.environ:
        return os.environ[env_option_name]

    try:
        return _parser.get(section, option)
    except NoOptionError:
        if failover_to_general:
            return _get('general', option)
        return None


def _load_config():
    parser = GlobusConfigParser()
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
