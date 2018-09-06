"""restmagic.parser"""
import re

from restmagic.request import RESTRequest


class ParseError(Exception):
    """Query parsing error occured."""


def parse_rest_request(text):
    """Parse HTTP query.

    :param text: full HTTP query string
    :returns: RESTRequest with parsed values
    :raises: ParseError
    """
    pattern = re.compile(r"""
    ^\s*  # possible whitespaces at the beginning
    (?P<method>\w+)\s+
    (?P<url>\S+)
    """, re.VERBOSE | re.MULTILINE)
    match = re.match(pattern, text)
    if not match:
        raise ParseError('Syntax error')
    # headers and body are separated by a blank line
    parts = text[match.end():].split('\n\n', 1)
    return RESTRequest(
        method=match.group('method').upper(),
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
