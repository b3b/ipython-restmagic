"""restmagic.display"""
import json
import sys
from IPython.display import display
from IPython.display import HTML, Image, Pretty, SVG

from restmagic.response import get_mime_type


LINE_MAGIC_USAGE = """%{magic} --insecure GET https://httpbin.org/json"""
CELL_MAGIC_USAGE = """%%{magic} --insecure
POST https://httpbin.org/post
Header: value

Message body, separated from headers by an empty line.
"""


def display_usage_example(magic, error_text, is_cell_magic):
    """Display magic usage example.
    :param magic: command name
    :parame error_text: text of an error to display
    :param is_cell_magic: display cell usage if True, else line magic usage
    """
    if error_text:
        print(error_text, file=sys.stderr)
        sys.stderr.flush()
    print("Usage example:")
    text = CELL_MAGIC_USAGE if is_cell_magic else LINE_MAGIC_USAGE
    display(HTML('<pre>' + text.format(magic=magic) + '</pre>'))


def display_dict(data):
    """Display the pretty representation of the dictionary.

    :param data: dict
    """
    display(Pretty(json.dumps(data, indent=2, ensure_ascii=False)))


def display_response(response):
    """Display the pretty representation of the given HTTP response.

    :param response: :class:`request.Response`
    """
    if not response.content:
        return
    mime_type = get_mime_type(response)
    if mime_type == 'application/json':
        display_dict(response.json())
    elif mime_type == 'text/html':
        display(HTML(response.text))
    elif mime_type == 'image/svg+xml':
        display(SVG(response.content))
    elif mime_type in ['image/png', 'image/jpeg', 'image/jpg']:
        display(Image(response.content))
    else:
        display(Pretty(response.text))
