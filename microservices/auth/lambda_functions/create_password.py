# create_password.py

from os import getenv
from typing import Any, Union

from boto3 import client

from utils.aws_lambda import construct_response

user_pool_client_id: str = getenv('USER_POOL_CLIENT_ID', '')
if not user_pool_client_id:
    raise RuntimeError('Environment variable \'USER_POOL_CLIENT_ID\' is not set')

cognito_client = client("cognito-idp")

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Union[int, dict[str, Any]]]:
    """
    Handles AWS Lambda function requests for creating a new password.

    :param event: Event data passed into the lambda function from the caller.
    :param context: A LambdaContext object that provides methods and properties about the
        invocation, function, and execution environment.
    :return: A dictionary containing the HTTP response.
    """
    try:
        username: str = event['username']
        new_password: str = event['newPassword']
        session: str = event['session']
    except KeyError as e:
        return construct_response(status_code=400, message=f'Missing parameters. Client error: {e}')

    try:
        response: dict[str, Any] = cognito_client.respond_to_auth_challenge(
            ClientId=user_pool_client_id,
            ChallengeName='NEW_PASSWORD_REQUIRED',
            ChallengeResponses={
                'USERNAME': username,
                'NEW_PASSWORD': new_password,
            },
            Session=session
        )

    except Exception as e:
        return construct_response(status_code=500, message=str(e))

    else:
        data: dict[str, Any] = {
            'accessToken': response['AuthenticationResult']['AccessToken'],
            'expiresIn': response['AuthenticationResult']['ExpiresIn'],
            'refreshToken': response['AuthenticationResult']['RefreshToken'],
        }

        print(f'{username} has confirmed their account successfully.')

        return construct_response(status_code=200, data=data)
