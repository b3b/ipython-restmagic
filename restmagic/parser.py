"""restmagic.parser"""
import re
from string import Template

import jsonpath_rw

from restmagic.request import RESTRequest


class ParseError(Exception):
    """Query parsing error occured."""


def expand_variables(text, kwargs):
    """Expand python variables in a string.

    :param text: string for processing
    :param kwargs: namespace for expansion
    :returns: new expanded string
    """
    return Template(text).safe_substitute(kwargs)


def parse_rest_request(text):
    """Parse HTTP query.

    :param text: full HTTP query string
    :returns: RESTRequest with parsed values
    :raises: ParseError
    """
    pattern = re.compile(r"""
    ^\s*  # possible whitespaces at the beginning
    ((?P<method>\w+)\s+)?  # optional method
    (?P<url>\S+)
    ([ \t]+HTTP/\d+[.]?\d*)?  # optional protocol version identification
    """, re.VERBOSE | re.MULTILINE)
    match = re.match(pattern, text)
    if not match:
        raise ParseError('Usage error')
    # headers and body are separated by a blank line
    parts = re.split(r'\n[ \t]*\n', text[match.end():], 1)
    return RESTRequest(
        method=(match.group('method') or '').upper(),
        url=match.group('url'),
        headers=parse_rest_headers(parts[0]),
        body=parts[1] if len(parts) > 1 else '',
    )


def parse_rest_headers(text):
    """Parse and validate HTTP headers.

    :param text: headers string
    :returns: dict -- parsed headers
    :raises: ParseError
    """
    pattern = re.compile(r"""
    (?P<name>\S+)
    [ \t]*:[ \t]*
    (?P<value>.+)
    $
    """, re.VERBOSE)
    headers = {}
    for line in text.splitlines():
        line = line.strip()
        if line:
            match = re.match(pattern, line)
            if not match:
                raise ParseError("Bad header: \"{0}\".".format(line))
            headers[match.group('name')] = match.group('value')
    return headers


def parse_response(response, expression):
    """Parse response with a given JSONPath expression.

    :param response: :class:`request.Response`
    :param expression: JSONPath query string
    :returns: dict -- parsed response
    :raises: jsonpath_rw.lexer.JsonPathLexerError, json.JSONDecodeError,
             Exception
    """
    data = response.json()
    return {
        str(match.full_path): match.value
        for match in jsonpath_rw.parse(expression).find(data)
    }
