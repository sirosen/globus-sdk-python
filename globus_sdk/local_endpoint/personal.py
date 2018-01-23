import os


def _on_windows():
    """
    Per python docs, this is a safe, reliable way of checking the platform.
    sys.platform offers more detail -- more than we want, in this case.
    """
    return os.name == "nt"


class LocalGlobusConnectPersonal(object):
    r"""
    A LocalGlobusConnectPersonal object represents the available SDK methods
    for inspecting and controlling a running Globus Connect Personal
    installation.

    These objects do *not* inherit from BaseClient and do not provide methods
    for interacting with any Globus Service APIs.
    """
    def __init__(self):
        self._endpoint_id = None

    @property
    def endpoint_id(self):
        """
        :type: string

        The endpoint ID of the local Globus Connect Personal endpoint
        installation.

        This value is loaded whenever it is first accessed, but saved after
        that. To reload the endpoint ID, either create a new
        LocalGlobusConnectPersonal, or delete the property with ``del``.

        Simple usage:

        >>> from globus_sdk import TransferClient, LocalGlobusConnectPersonal
        >>> local_ep = LocalGlobusConnectPersonal()
        >>> ep_id = local_ep.endpoint_id
        >>> tc = TransferClient(...)  # needs auth details
        >>> for f in tc.operation_ls(ep_id):
        >>>     print("Local file: ", f["name"])

        Example of using ``del`` to reset the endpoint ID:

        >>> local_ep = LocalGlobusConnectPersonal()
        >>> x = local_ep.endpoint_id  # endpoint_id is now saved
        >>>
        >>> # while code is running, reinstall Globus Connect Personal,
        >>> # thus generating a new endpoint ID
        >>>
        >>> assert x == local_ep.endpoint_id  # the value has not changed
        >>> del local_ep.endpoint_id  # clear the endpoint_id , allowing it to
        >>>                           # reload
        >>>
        >>> y = local_ep.endpoint_id  # y will now have the new value
        >>> assert x != y  # and the value has changed, x still has the old val
        """
        if self._endpoint_id is None:
            try:
                if _on_windows():
                    appdata = os.getenv("LOCALAPPDATA")
                    if appdata is None:
                        raise ValueError(
                            "LOCALAPPDATA not detected in Windows environment")
                    fname = os.path.join(
                        appdata, "Globus Connect\client-id.txt")
                else:
                    fname = os.path.expanduser(
                        "~/.globusonline/lta/client-id.txt")
                with open(fname) as fp:
                    self._endpoint_id = fp.read().strip()
            except IOError as e:
                # no such file or directory
                if e.errno == 2:
                    pass
                else:
                    raise

        return self._endpoint_id

    @endpoint_id.deleter
    def endpoint_id(self):
        """
        Deleter for LocalGlobusConnectPersonal.endpoint_id
        """
        self._endpoint_id = None
