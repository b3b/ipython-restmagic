"""restmagic.parser"""
import json
import re
from string import Template
from typing import Any, Callable, Dict

import jsonpath_rw
from lxml import etree
from requests import Response

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


def parse_json_response(*, response, expression):
    """Parse response with a given JSONPath expression.

    :param response: :class:`request.Response`
    :param expression: JSONPath query string
    :returns: dict -- parsed response
    :raises: jsonpath_rw.lexer.JsonPathLexerError, json.JSONDecodeError,
    """
    data = response.json()
    return {
        str(match.full_path): match.value
        for match in jsonpath_rw.parse(expression).find(data)
    }


class XPathParser:
    """Parser for XML and HTML responses.

    :cvar parsers: mapping of supported content subtypes to lxml parsers
    """

    parsers = {
        'html': etree.HTML,
        'xml': etree.XML,
    }

    def __init__(self, content_subtype: str):
        self.parser: Callable[[str], etree._Element] = self.parsers[content_subtype]

    def __call__(self, *, response: Response, expression: str) -> Dict[str, Any]:
        """Parse response with a given XPath expression.

        :param response: HTTP response to parse
        :param expression: XPath query string
        :returns: parsed response
        :raises: etree.LxmlError
        """
        root: etree._Element = self.parser(response.content)
        if root is not None:
            tree: etree._ElementTree = root.getroottree()
            return {
                tree.getpath(element): etree.tostring(
                    element, encoding='unicode', pretty_print=True
                )
                for element in root.xpath(expression)
            }
        return {}


def guess_response_content_subtype(response: Response) -> str:
    """Returns guessed content subtype of a HTTP response.
    """
    try:
        response.json()
    except json.JSONDecodeError:
        return 'html'
    return 'json'


class ResponseParser:
    """HTTP response parser. Extracts parts of response content.

    :cvar parsers: mapping of supported content subtypes to parsers
    """

    parsers = {
        'json': parse_json_response,
        'xml': XPathParser('xml'),
        'html': XPathParser('html'),
    }

    def __init__(self, *, response: Response, expression: str, content_subtype: str = None):
        if not content_subtype:
            content_subtype = guess_response_content_subtype(response)
        self.parser = self.parsers[content_subtype]
        self.response = response
        self.expression = expression

    def parse(self) -> Dict[str, Any]:
        """Perform parsing."""
        return self.parser(response=self.response, expression=self.expression)
