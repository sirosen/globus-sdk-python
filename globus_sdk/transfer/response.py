import json

from globus_sdk.response import GlobusHTTPResponse


class TransferResponse(GlobusHTTPResponse):
    """
    Custom response for TransferClient, which relies on the fact that the
    body is always json to make printing the response more friendly.
    """
    def __str__(self):
        return json.dumps(self.data, indent=2)


class IterableTransferResponse(TransferResponse):
    def __iter__(self):
        return iter(self['DATA'])
