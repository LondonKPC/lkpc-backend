# create_password.py
from typing import Any, Union

from microservices.auth.lambda_functions.login import cognito_client
from utils.aws_lambda import construct_response

from boto3 import client

cognito_client: CognitoIdentityProviderClient =

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
        password: str = event['password']
        session: str = event['session']
            except KeyError as e:
        return construct_response(status_code=400, message=f'Missing parameters. Client error: {e}')

    try:
