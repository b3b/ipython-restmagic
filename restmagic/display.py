"""restmagic.display"""
import json
from IPython.display import display
from IPython.display import HTML, Image, Pretty, SVG


def display_response(response):
    """Display the pretty representation of the given HTTP response.

    :param response: :class:`request.Response`
    """
    mime_type = get_mime_type(response)
    if mime_type == 'application/json':
        display(Pretty(json.dumps(response.json(), indent=2)))
    elif mime_type == 'text/html':
        display(HTML(response.text))
    elif mime_type == 'image/svg+xml':
        display(SVG(response.content))
    elif mime_type in ['image/png', 'image/jpeg', 'image/jpg']:
        display(Image(response.content))
    else:
        display(Pretty(response.text))


def get_mime_type(response):
    """Returns the MIME type of the given HTTP response.

    :param response: :class:`request.Response`
    """
    content_type = response.headers.get('content-type')
    if content_type:
        return content_type.split(';')[0].strip().lower()
    return None
