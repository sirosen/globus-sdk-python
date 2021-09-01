import uuid
from typing import Any, Callable, Dict, Iterable, Optional, TypeVar, Union

from globus_sdk import client, response, scopes, utils
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.types import UUIDLike

from .errors import GCSAPIError
from .response import IterableGCSResponse, UnpackingGCSResponse

RT = TypeVar("RT")


def _gcsdoc(
    message: str, link: str
) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    # do not use functools.partial because it doesn't preserve type information
    # see: https://github.com/python/mypy/issues/1484
    def partial(func: Callable) -> Callable:
        return utils.doc_api_method(
            message,
            link,
            external_base_url="https://docs.globus.org/globus-connect-server/v5/api",
        )(func)

    return partial


class GCSClient(client.BaseClient):
    """
    A GCSClient provides communication with the GCS Manager API of a Globus Connect
    Server instance.
    For full reference, see the `documentation for the GCS Manager API
    <https://docs.globus.org/globus-connect-server/v5/api/>`_.

    Unlike other client types, this must be provided with an address for the GCS
    Manager. All other arguments are the same as those for `~globus_sdk.BaseClient`.

    :param gcs_address: The FQDN (DNS name) or HTTPS URL for the GCS Manager API.
    :type gcs_address: str

    .. automethodlist:: globus_sdk.GCSClient
    """

    service_name = "globus_connect_server"
    error_class = GCSAPIError

    def __init__(
        self,
        gcs_address: str,
        *,
        environment: Optional[str] = None,
        authorizer: Optional[GlobusAuthorizer] = None,
        app_name: Optional[str] = None,
        transport_params: Optional[Dict] = None,
    ):
        # check if the provided address was a DNS name or an HTTPS URL
        # if it was a URL, do not modify, but if it's a DNS name format it accordingly
        # as a heuristic for this: just check if string starts with "https://" (this is
        # sufficient to distinguish between the two for valid inputs)
        if not gcs_address.startswith("https://"):
            gcs_address = f"https://{gcs_address}/api/"
        super().__init__(
            base_url=gcs_address,
            environment=environment,
            authorizer=authorizer,
            app_name=app_name,
            transport_params=transport_params,
        )

    @staticmethod
    def get_gcs_endpoint_scopes(
        endpoint_id: Union[uuid.UUID, str]
    ) -> scopes.GCSEndpointScopeBuilder:
        """Given a GCS Endpoint ID, this helper constructs an object containing the
        scopes for that Endpoint.

        :param endpoint_id: The ID of the Endpoint
        :type endpoint_id: UUID or str

        See documentation for :class:`globus_sdk.scopes.GCSEndpointScopeBuilder` for
        more information.
        """
        return scopes.GCSEndpointScopeBuilder(str(endpoint_id))

    @staticmethod
    def get_gcs_collection_scopes(
        collection_id: Union[uuid.UUID, str]
    ) -> scopes.GCSCollectionScopeBuilder:
        """Given a GCS Collection ID, this helper constructs an object containing the
        scopes for that Collection.

        :param collection_id: The ID of the Collection
        :type collection_id: UUID or str

        See documentation for :class:`globus_sdk.scopes.GCSCollectionScopeBuilder` for
        more information.
        """
        return scopes.GCSCollectionScopeBuilder(str(collection_id))

    @_gcsdoc("List Collections", "openapi_Collections/#ListCollections")
    def get_collection_list(
        self,
        *,
        include: Union[str, Iterable[str], None] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableGCSResponse:
        """
        ``GET /collections``

        :param include: Names of additional documents to include in the response
        :type include: str or iterable of str, optional
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        List the Collections on an Endpoint
        """
        if query_params is None:
            query_params = {}
        if include is not None:
            if isinstance(include, str):
                include = [include]
            query_params["include"] = ",".join(include)
        return IterableGCSResponse(self.get("collections", query_params=query_params))

    @_gcsdoc("Get Collection", "openapi_Collections/#getCollection")
    def get_collection(
        self,
        collection_id: UUIDLike,
        *,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> UnpackingGCSResponse:
        """
        ``GET /collections/{collection_id}``

        :param collection_id: The ID of the collection to lookup
        :type collection_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional

        Lookup a Collection on an Endpoint
        """
        collection_id = utils.safe_stringify(collection_id)
        return UnpackingGCSResponse(
            self.get(f"/collections/{collection_id}", query_params=query_params),
            r"collection#1\.\d+\.\d+",
        )

    def delete_collection(
        self,
        collection_id: UUIDLike,
        *,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /collections/{collection_id}``

        :param collection_id: The ID of the collection to delete
        :type collection_id: str or UUID
        :param query_params: Additional passthrough query parameters
        :type query_params: dict, optional
        """
        collection_id = utils.safe_stringify(collection_id)
        return self.delete(f"/collections/{collection_id}", query_params=query_params)
