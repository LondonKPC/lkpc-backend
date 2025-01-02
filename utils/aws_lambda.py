from typing import Any, Optional


def construct_response(status_code: int, message: Optional[str] = None, data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    response: dict[str, Any] = {
        'header': {
            'Content-Type': 'application/json',
        },
        'statusCode': status_code,
        'body': {}
    }

    if not data:
        data = {}

    # Put the data in the response body
    if status_code == 200:
        # If there is a message, put the message into the response body
        if message:
            response['body']['message'] = message

        # If there is data, put the data into the response body
        if data:
            # This prevents extra layers of nesting
            response['body'] = {**response['body'], **data}

    # Otherwise it's an error, so construct an error into response body
    else:
        response['body']['error'] = message

    # If there is nothing to put into the response body, remove it from the response
    if not response['body']:
        del response['body']

    return response
