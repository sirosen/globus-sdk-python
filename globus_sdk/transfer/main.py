"""
Facilitate using the TransferClient in an ipython shell. Creates global
variable `tc` which is an instance of TransferClient.

Example usage:
    $ ipython -i -mglobus_sdk.transfer.main -- [-f /path/to/token] [-e env]
    In [1]: for ep in tc.endpoint_search(filter_scope='my-endpoints'):
    ...         print(ep)
"""
from __future__ import print_function

import argparse

import globus_sdk


def get_transfer_client_from_args(args=None):
    parser = argparse.ArgumentParser(
                description="Interactive shell for TransferClient")
    parser.add_argument("-f", "--token-file",
                        help="path to a file containing an auth token")
    parser.add_argument("-e", "--environment",
                        help="connect to an alternate environment")
    args = parser.parse_args(args)

    token = None
    if args.token_file:
        with open(args.token_file) as f:
            token = f.read().strip()

    environment = "default"
    if args.environment:
        environment = args.environment

    authorizer = None
    if token is not None:
        authorizer = globus_sdk.AccessTokenAuthorizer(token)
    client = globus_sdk.TransferClient(environment, authorizer=authorizer)
    return client


if __name__ == '__main__':
    tc = get_transfer_client_from_args()
