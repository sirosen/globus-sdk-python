"""
The GCSDownloader provides HTTPS file download capabilities for Globus Connect Server.
"""

from __future__ import annotations

import typing as t
import urllib.parse

import globus_sdk
import globus_sdk.scopes
import globus_sdk.transport
from globus_sdk import client, utils
from globus_sdk.authorizers import GlobusAuthorizer


class GCSDownloader:
    def __init__(
        self,
        app: globus_sdk.GlobusApp,
        *,
        client: GCSCollectionHTTPSClient | None = None,
        transport: globus_sdk.transport.RequestsTransport | None = None,
    ) -> None:
        self.app = app
        self.transport: globus_sdk.transport.RequestsTransport = (
            transport or globus_sdk.transport.RequestsTransport()
        )

        self.client = client

    @t.overload
    def read_file(self, file_uri: str, *, as_text: t.Literal[True]) -> str: ...
    @t.overload
    def read_file(self, file_uri: str, *, as_text: t.Literal[False]) -> bytes: ...
    @t.overload
    def read_file(self, file_uri: str) -> str: ...

    def read_file(self, file_uri: str, *, as_text: bool = True) -> str | bytes:
        """
        Given a file URI on a GCS Collection, read the data.
        """
        response = self._read_file(file_uri)
        if as_text:
            return response.text
        return response.binary_content

    def _read_file(self, file_uri: str) -> globus_sdk.GlobusHTTPResponse:
        if self.client is None:
            self.client = self.get_client_from_uri(file_uri)
        return self.client.get(file_uri)

    def get_client_from_uri(self, file_uri: str) -> GCSCollectionHTTPSClient:
        collection_id = self._sniff_collection_id(file_uri)
        scopes = self._detect_scopes(collection_id)

        base_url = _get_base_url(file_uri)

        return GCSCollectionHTTPSClient(
            collection_id, scopes, app=self.app, base_url=base_url
        )

    def _detect_scopes(self, collection_id: str) -> list[globus_sdk.Scope]:
        transfer_client = globus_sdk.TransferClient(app=self.app)

        builder = globus_sdk.scopes.GCSCollectionScopeBuilder(collection_id)
        if _uses_data_access(transfer_client, collection_id):
            return [
                globus_sdk.Scope(builder.https),
                globus_sdk.Scope(builder.data_access),
            ]
        return [globus_sdk.Scope(builder.https)]

    def _sniff_collection_id(self, file_uri: str) -> str:
        response = self.transport.request("GET", file_uri, allow_redirects=False)
        if "Location" not in response.headers:
            msg = (
                f"Attempting to detect the collection ID for the file at '{file_uri}' "
                "failed. Did not receive a redirect with Location header on "
                "unauthenticated call."
            )
            raise RuntimeError(msg)

        location_header = response.headers["Location"]
        parsed_location = urllib.parse.urlparse(location_header)
        parsed_location_qs = urllib.parse.parse_qs(parsed_location.query)

        if "client_id" not in parsed_location_qs:
            msg = (
                f"Attempting to detect the collection ID for the file at '{file_uri}' "
                "failed. Location header did not encode a 'client_id'."
            )
            raise RuntimeError(msg)

        client_ids = parsed_location_qs["client_id"]
        if len(client_ids) != 1:
            msg = (
                f"Attempting to detect the collection ID for the file at '{file_uri}' "
                "failed. Multiple 'client_id' params were present."
            )
            raise RuntimeError(msg)

        return client_ids[0]


class GCSCollectionHTTPSClient(globus_sdk.BaseClient):
    def __init__(
        self,
        collection_client_id: str,
        default_scope_requirements: t.Iterable[globus_sdk.Scope] = (),
        *,
        base_url: str,
        environment: str | None = None,
        app: globus_sdk.GlobusApp | None = None,
        app_scopes: list[globus_sdk.Scope] | None = None,
        authorizer: GlobusAuthorizer | None = None,
        app_name: str | None = None,
        transport_params: dict[str, t.Any] | None = None,
    ) -> None:
        self.collection_client_id = collection_client_id
        self._default_scope_requirements = list(default_scope_requirements)
        super().__init__(
            environment=environment,
            base_url=base_url,
            app=app,
            app_scopes=app_scopes,
            authorizer=authorizer,
            app_name=app_name,
            transport_params=transport_params,
        )

    @utils.classproperty
    def resource_server(  # pylint: disable=missing-param-doc
        self_or_cls: client.BaseClient | type[client.BaseClient],
    ) -> str | None:
        """
        The resource server for a GCS collection is the ID of the collection.

        This will return None if called as a classmethod as an instantiated
        ``GCSClient`` is required to look up the client ID from the endpoint.
        """
        if not isinstance(self_or_cls, GCSCollectionHTTPSClient):
            return None

        return self_or_cls.collection_client_id

    @property
    def default_scope_requirements(self) -> list[globus_sdk.Scope]:
        return self._default_scope_requirements


def _get_base_url(file_uri: str) -> str:
    parsed = urllib.parse.urlparse(file_uri)
    return f"{parsed.scheme}://{parsed.netloc}"


def _uses_data_access(
    transfer_client: globus_sdk.TransferClient, collection_id: str
) -> bool:
    doc = transfer_client.get_endpoint(collection_id)
    if doc["entity_type"] != "GCSv5_mapped_collection":
        return False
    if doc["high_assurance"]:
        return False
    return True
