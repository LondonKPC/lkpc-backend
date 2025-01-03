# login.py
# Handles login logic by receiving an event (username, password) and verifying auth with the cognito user pool.

from os import getenv
from typing import Any, Union

from boto3 import client
from mypy_boto3_cognito_idp.client import CognitoIdentityProviderClient
from mypy_boto3_cognito_idp.type_defs import InitiateAuthResponseTypeDef

from utils.aws_lambda import construct_response

user_pool_client_id: str = getenv('USER_CLIENT_ID', '')
if not user_pool_client_id:
    raise RuntimeError('Environment variable \'USER_CLIENT_ID\' is not set.')

# Get cognito client
cognito_client: CognitoIdentityProviderClient = client('cognito-idp')

# TODO: Eventually make a function to send an error response to the frontend
# TODO: Add logging

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Union[int, dict[str, Any]]]:
    """
    Lambda handler for user login. Initiates authentication flow for the user. If the user is required to
    change their password, the response will include a session token. Otherwise, the response will include the access
    token, ID token, refresh token, and expiration time.

    :param event: Event data passed into the lambda function from the caller.
    :param context: A LambdaContext object that provides methods and properties about the
        invocation, function, and execution environment.
    :return: A dictionary containing the HTTP response.
    """
    try:
        # Get the username and password from the event
        username: str = event['username']
        password: str = event['password']
    except KeyError as e:
        # client error (400): username or password was not found or entered
        print(f'Login failed. Missing required parameters: {e}')
        return construct_response(status_code=400, message=f'Login failed. Missing required parameters: {e}')
    try:
        # Attempt to authenticate with cognito identity pool
        response: InitiateAuthResponseTypeDef = cognito_client.initiate_auth(
            ClientId=user_pool_client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': username, 'PASSWORD': password}
        )

    except Exception as e:
        # Cognito login failed
        print(f'Login failed for `{username}`. Cognito exception: {e}')
        return construct_response(status_code=500, message=f'Login failed for `{username}`. Cognito exception: {e}')

    data: dict[str, Any] = {}
    if 'ChallengeName' in response and response['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
        data['newPasswordRequired'] = True
        data['sessionToken'] = response['Session']
        print(f'Login successful for `{username}. New password required.')
    else:
        data['accessToken'] = response['AuthenticationResult']['AccessToken']
        data['idToken'] = response['AuthenticationResult']['IdToken']
        data['refreshToken'] = response['AuthenticationResult']['RefreshToken']
        data['expiresIn'] = response['AuthenticationResult']['ExpiresIn']
        print(f'Login successful for `{username}.')

    return construct_response(status_code=200, data=data)
