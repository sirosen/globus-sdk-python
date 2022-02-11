import importlib
from typing import Any, Dict, Iterator, Optional, Union

import responses

from ..utils import slash_join


class RegisteredResponse:
    _url_map = {
        "auth": "https://auth.globus.org/",
        "nexus": "https://nexus.api.globusonline.org/",
        "transfer": "https://transfer.api.globus.org/v0.10",
        "search": "https://search.api.globus.org/",
        "gcs": "https://abc.xyz.data.globus.org/api",
        "groups": "https://groups.api.globus.org/v2/",
    }

    def __init__(
        self,
        service: str,
        path: str,
        method: str = responses.GET,
        headers: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        body: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.service = service
        self.path = path
        self.full_url = slash_join(self._url_map[service], path)

        self.method = method
        self.json = json
        self.body = body

        if headers is None:
            headers = {"Content-Type": "application/json"}
        self.headers = headers

        self.metadata = metadata or {}
        self.kwargs = kwargs

    def _set_response(self, *, replace: bool) -> None:
        kwargs = {"headers": self.headers, "match_querystring": False, **self.kwargs}
        if self.json is not None:
            kwargs["json"] = self.json
        if self.body is not None:
            kwargs["body"] = self.body

        if replace:
            func = responses.replace
        else:
            func = responses.add
        func(self.method, self.full_url, **kwargs)

    def add(self) -> None:
        self._set_response(replace=False)

    def replace(self) -> None:
        self._set_response(replace=True)


class ResponseSet:
    def __init__(
        self,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: RegisteredResponse,
    ) -> None:
        self.metadata = metadata
        self._data: Dict[str, RegisteredResponse] = {**kwargs}

    def register(self, case: str, value: RegisteredResponse) -> None:
        self._data[case] = value

    def lookup(self, case: str) -> RegisteredResponse:
        try:
            return self._data[case]
        except KeyError as e:
            raise Exception("did not find a matching registered response") from e

    def __bool__(self) -> bool:
        return bool(self._data)

    def __iter__(self) -> Iterator[RegisteredResponse]:
        return iter(self._data.values())

    def activate(self, case: str, *, replace: bool = False) -> RegisteredResponse:
        res = self.lookup(case)
        if replace:
            res.replace()
        else:
            res.add()
        return res

    def activate_all(self) -> None:
        for x in self:
            x.add()

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Dict[str, Dict[str, Any]],
    ) -> "ResponseSet":
        # constructor which expects native dicts and converts them to RegisteredResponse
        # objects, then puts them into the ResponseSet
        return cls(
            metadata=metadata, **{k: RegisteredResponse(**v) for k, v in data.items()}
        )


_RESPONSE_SET_REGISTRY: Dict[str, ResponseSet] = {}


def register_response_set(
    name: str,
    rset: Union[ResponseSet, Dict[str, Dict[str, Any]]],
    metadata: Optional[Dict[str, Any]] = None,
) -> ResponseSet:
    if isinstance(rset, dict):
        rset = ResponseSet.from_dict(rset, metadata=metadata)
    _RESPONSE_SET_REGISTRY[name] = rset
    return rset


def get_response_set(name: str) -> ResponseSet:
    # first priority: check the explicit registry
    if name in _RESPONSE_SET_REGISTRY:
        return _RESPONSE_SET_REGISTRY[name]
    # after that, check the built-in "registry" built from modules
    module = importlib.import_module(f"globus_sdk._testing.data.{name}")
    assert isinstance(module.RESPONSES, ResponseSet)
    return module.RESPONSES
