import io

import requests


def response_with_content(content, headers=None):
    response = requests.Response()
    response.raw = io.BytesIO(content)
    response.headers = headers or {}
    return response
