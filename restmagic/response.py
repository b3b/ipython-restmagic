"""restmagic.response"""
import json
from typing import Optional

from requests import Response


def get_mime_type(response: Response) -> Optional[str]:
    """Returns the MIME type of the given HTTP response.

    :param response: :class:`request.Response`
    """
    content_type = response.headers.get('content-type')
    if content_type:
        return content_type.split(';')[0].strip().lower()
    return None


def guess_response_content_subtype(
        response: Response
) -> Optional[str]:
    """Returns the guessed content subtype of the given HTTP response.
    """
    mime = get_mime_type(response)
    if mime:
        subtype = mime.split('/')[-1]
        for known_subtype in 'json', 'html', 'xml':
            if known_subtype in subtype:
                return known_subtype
    try:
        response.json()
    except json.JSONDecodeError:
        return None
    return 'json'
