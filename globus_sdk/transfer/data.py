"""
Data helper classes for constructing Transfer API documents. All classes should
extend ``dict``, so they can be passed seemlesly to
:class:`TransferClient <globus_sdk.TransferClient>` methods without
conversion.
"""
import logging

from globus_sdk.base import safe_stringify

logger = logging.getLogger(__name__)


class TransferData(dict):
    """
    Convenience class for constructing a transfer document, to use as the
    `data` parameter to
    :meth:`submit_transfer <globus_sdk.TransferClient.submit_transfer>`.

    At least one item must be added using
    :meth:`add_item <globus_sdk.TransferData.add_item>`.

    For compatibility with older code and those knowledgeable about the API
    sync_level can be ``0``, ``1``, ``2``, or ``3``, but it can also be
    ``"exists"``, ``"size"``, ``"mtime"``, or ``"checksum"`` if you want
    greater clarity in client code.

    Includes fetching the submission ID as part of document generation. The
    submission ID can be pulled out of here to inspect, but the document
    can be used as-is multiple times over to retry a potential submission
    failure (so there shouldn't be any need to inspect it).

    See the
    :meth:`submit_transfer <globus_sdk.TransferClient.submit_transfer>`
    documentation for example usage.
    """
    def __init__(self, transfer_client, source_endpoint, destination_endpoint,
                 label=None, sync_level=None, **kwargs):
        source_endpoint = safe_stringify(source_endpoint)
        destination_endpoint = safe_stringify(destination_endpoint)
        logger.info("Creating a new TransferData object")
        self["DATA_TYPE"] = "transfer"
        self["submission_id"] = transfer_client.get_submission_id()["value"]
        logger.info("TransferData.submission_id = {}"
                    .format(self["submission_id"]))
        self["source_endpoint"] = source_endpoint
        logger.info("TransferData.source_endpoint = {}"
                    .format(source_endpoint))
        self["destination_endpoint"] = destination_endpoint
        logger.info("TransferData.destination_endpoint = {}"
                    .format(destination_endpoint))

        if label is not None:
            self["label"] = label
            logger.debug("TransferData.label = {}".format(label))

        # map the sync_level (if it's a nice string) to one of the known int
        # values
        # you can get away with specifying an invalid sync level -- the API
        # will just reject you with an error. This is kind of important: if
        # more levels are added in the future this method doesn't become
        # garbage overnight
        if sync_level is not None:
            sync_dict = {"exists": 0, "size": 1, "mtime": 2, "checksum": 3}
            self['sync_level'] = sync_dict.get(sync_level, sync_level)
            logger.info("TransferData.sync_level = {} ({})"
                        .format(self['sync_level'], sync_level))

        self["DATA"] = []

        self.update(kwargs)

    def add_item(self, source_path, destination_path, recursive=False):
        """
        Add a file or directory to be transfered.

        Appends a transfer_item document to the DATA key of the transfer
        document.
        """
        item_data = {
            "DATA_TYPE": "transfer_item",
            "source_path": source_path,
            "destination_path": destination_path,
            "recursive": recursive,
        }
        logger.debug('TransferData[{}, {}].add_item: "{}"->"{}"'
                     .format(self["source_endpoint"],
                             self["destination_endpoint"],
                             source_path, destination_path))
        self["DATA"].append(item_data)


class DeleteData(dict):
    """
    Convenience class for constructing a delete document, to use as the
    `data` parameter to
    :meth:`submit_delete <globus_sdk.TransferClient.submit_delete>`.

    At least one item must be added using
    :meth:`add_item <globus_sdk.DeleteData.add_item>`.

    Includes fetching the submission ID as part of document generation. The
    submission ID can be pulled out of here to inspect, but the document
    can be used as-is multiple times over to retry a potential submission
    failure (so there shouldn't be any need to inspect it).

    See the :meth:`submit_delete <globus_sdk.TransferClient.submit_delete>`
    documentation for example usage.
    """
    def __init__(self, transfer_client, endpoint, label=None,
                 recursive=False, **kwargs):
        endpoint = safe_stringify(endpoint)
        logger.info("Creating a new DeleteData object")
        self["DATA_TYPE"] = "delete"
        self["submission_id"] = transfer_client.get_submission_id()["value"]
        logger.info("DeleteData.submission_id = {}"
                    .format(self["submission_id"]))
        self["endpoint"] = endpoint
        logger.info("DeleteData.endpoint = {}"
                    .format(endpoint))
        self["recursive"] = recursive
        logger.info("DeleteData.recursive = {}"
                    .format(recursive))

        if label is not None:
            self["label"] = label
            logger.debug("DeleteData.label = {}".format(label))

        self["DATA"] = []
        self.update(kwargs)

    def add_item(self, path):
        """
        Add a file or directory to be deleted. If any of the paths are
        directories, ``recursive`` must be set True on the top level
        ``DeleteData``.

        Appends a delete_item document to the DATA key of the delete
        document.
        """
        item_data = {
            "DATA_TYPE": "delete_item",
            "path": path,
        }
        logger.debug('DeleteData[{}].add_item: "{}"'
                     .format(self["endpoint"], path))
        self["DATA"].append(item_data)
