#!/usr/bin/env python

from globus_sdk import NativeAppAuthClient


CLIENT_ID = 'd0f1d9b0-bd81-4108-be74-ea981664453a'
SCOPES = ('openid profile email '
          'urn:globus:auth:scope:transfer.api.globus.org:all')

get_input = getattr(__builtins__, 'raw_input', input)


client = NativeAppAuthClient(client_id=CLIENT_ID)
client.oauth2_start_flow_native_app(requested_scopes=SCOPES,
                                    refresh_tokens=True)
url = client.oauth2_get_authorize_url()

print('Native App Authorization URL: \n{}'.format(url))
auth_code = get_input('Enter the auth code: ').strip()

tokens = client.oauth2_exchange_code_for_tokens(auth_code).by_resource_server

transfer_token = tokens['transfer.api.globus.org']['refresh_token']
auth_token = tokens['auth.globus.org']['refresh_token']

print('Transfer Token: {}'.format(transfer_token))
print('Auth Token    : {}'.format(auth_token))
