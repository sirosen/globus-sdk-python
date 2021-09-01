import base64
import os
import shlex
import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union, cast, overload

from globus_sdk.exc import GlobusSDKUsageError

if TYPE_CHECKING:
    import globus_sdk


_GRIDMAP_DN_START = '"/C=US/O=Globus Consortium/OU=Globus Connect User/CN='


class _B32DecodeError(ValueError):
    """custom exception type"""


def _b32decode(v: str) -> str:
    # should start with "u_"
    if not v.startswith("u_"):
        raise _B32DecodeError("should start with 'u_'")
    v = v[2:]
    # wrong length
    if len(v) != 26:
        raise _B32DecodeError("wrong length")

    # append padding and uppercase so that b32decode will work
    v = v.upper() + (6 * "=")

    # try to decode
    try:
        return str(uuid.UUID(bytes=base64.b32decode(v)))
    # if it fails, then it can't be a b32-encoded identity
    except ValueError:
        raise _B32DecodeError("decode and load as UUID failed")


def _on_windows() -> bool:
    """
    Per python docs, this is a safe, reliable way of checking the platform.
    sys.platform offers more detail -- more than we want, in this case.
    """
    return os.name == "nt"


class LocalGlobusConnectPersonal:
    r"""
    A LocalGlobusConnectPersonal object represents the available SDK methods
    for inspecting and controlling a running Globus Connect Personal
    installation.

    These objects do *not* inherit from BaseClient and do not provide methods
    for interacting with any Globus Service APIs.
    """

    def __init__(self) -> None:
        self._endpoint_id: Optional[str] = None
        self._cached_local_data_dir: Optional[str] = None

    # because fetching the local data dir can error, defer finding it into a property
    # with caching behavior
    @property
    def _local_data_dir(self) -> str:
        if self._cached_local_data_dir is None:
            if _on_windows():
                appdata = os.getenv("LOCALAPPDATA")
                if appdata is None:
                    raise GlobusSDKUsageError(
                        "LOCALAPPDATA not detected in Windows environment"
                    )
                self._cached_local_data_dir = os.path.join(appdata, "Globus Connect")
            else:
                self._cached_local_data_dir = os.path.expanduser("~/.globusonline/lta")

        return self._cached_local_data_dir

    def _ensure_local_data_dir(self) -> None:
        # force property evaluation to catch any errors
        # this wrapper is just an "imperative looking" way of doing this
        self._local_data_dir

    @overload
    def get_owner_info(self) -> Optional[Tuple[str, bool]]:
        ...

    @overload
    def get_owner_info(self, auth_client: None) -> Optional[Tuple[str, bool]]:
        ...

    @overload
    def get_owner_info(
        self, auth_client: "globus_sdk.AuthClient"
    ) -> Optional[Dict[str, Any]]:
        ...

    def get_owner_info(
        self, auth_client: Optional["globus_sdk.AuthClient"] = None
    ) -> Union[None, Tuple[str, bool], Dict[str, Any]]:
        """
        Look up the local GCP information.
        This method may return a username or a user ID. For that reason, the result is a
        tuple: (user, is_id).

        If you pass an AuthClient, this method will return a dict from the Get
        Identities API instead of the tuple. This can fail (e.g. with network errors if
        there is no connectivity), so passing this value should be coupled with
        additional error handling.

        In either case, the result may be ``None`` if the data is missing or cannot be
        parsed.

        .. note::

            The data returned by this method is not checked for accuracy. It is
            possible for a user to modify the files used by GCP to list a different
            user.

        :param auth_client: An AuthClient to use to lookup the full identity information
            for the GCP owner
        :type auth_client: globus_sdk.AuthClient

        **Examples**

        Getting a username:

        >>> from globus_sdk import LocalGlobusConnectPersonal
        >>> local_gcp = LocalGlobusConnectPersonal()
        >>> local_gcp.get_owner_info()
        ('foo@globusid.org', False)

        or you may get back an ID:

        >>> local_gcp = LocalGlobusConnectPersonal()
        >>> local_gcp.get_owner_info()
        ('7deda7cc-077b-11ec-a137-67523ecffd4b', True)
        """
        self._ensure_local_data_dir()

        fname = os.path.join(self._local_data_dir, "gridmap")
        try:
            # extract the first line which looks like a gridmap CN for GCP
            # all other lines will be ignored to accommodate cases where users have
            # modified their gridmap files in various ways (which GCP may or may not
            # support)
            data = None
            with open(fname) as fp:
                for line in fp:
                    if line.startswith(_GRIDMAP_DN_START):
                        data = line.strip()
                        break
        except OSError as e:
            # no such file or directory
            if e.errno == 2:
                return None
            raise

        # a gridmap CN line was not found
        if not data:
            return None

        lineinfo = shlex.split(data)
        if len(lineinfo) != 2:
            return None

        dn, _local_username = lineinfo
        username_or_id = dn.split("=", 4)[-1]

        try:
            user, is_id = _b32decode(username_or_id), True
        except _B32DecodeError:
            user, is_id = f"{username_or_id}@globusid.org", False

        if auth_client is None:
            return (user, is_id)

        if is_id:
            res = auth_client.get_identities(ids=user)
        else:
            res = auth_client.get_identities(usernames=user)

        try:  # could get no data back in theory, if the identity isn't visible
            return cast(Dict[str, Any], res["identities"][0])
        except (KeyError, IndexError):
            return None

    @property
    def endpoint_id(self) -> Optional[str]:
        """
        :type: str

        The endpoint ID of the local Globus Connect Personal endpoint
        installation.

        This value is loaded whenever it is first accessed, but saved after
        that.

        .. note::

            This attribute is not checked for accuracy. It is possible for a user to
            modify the files used by GCP to list a different ``endpoint_id``.

        Usage:

        >>> from globus_sdk import TransferClient, LocalGlobusConnectPersonal
        >>> local_ep = LocalGlobusConnectPersonal()
        >>> ep_id = local_ep.endpoint_id
        >>> tc = TransferClient(...)  # needs auth details
        >>> for f in tc.operation_ls(ep_id):
        >>>     print("Local file: ", f["name"])

        You can also reset the value, causing it to load again on next access,
        with ``del local_ep.endpoint_id``
        """
        if self._endpoint_id is None:
            self._ensure_local_data_dir()

            fname = os.path.join(self._local_data_dir, "client-id.txt")
            try:
                with open(fname) as fp:
                    self._endpoint_id = fp.read().strip()
            except OSError as e:
                # no such file or directory gets ignored, everything else reraise
                if e.errno != 2:
                    raise
        return self._endpoint_id

    @endpoint_id.deleter
    def endpoint_id(self) -> None:
        """
        Deleter for LocalGlobusConnectPersonal.endpoint_id
        """
        self._endpoint_id = None
