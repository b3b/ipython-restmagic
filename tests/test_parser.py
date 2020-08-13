import pytest

from restmagic.parser import (
    ParseError,
    RESTRequest,
    XPathParser,
    ResponseParser,
    UnknownSubtype,
    expand_variables,
    parse_rest_request,
    parse_json_response,
    remove_argument_quotes,
)

from .utils import response_with_content


@pytest.fixture
def json_response():
    return response_with_content(b"""
        {"store": {
            "book": [
                {
                    "title": "Book 1"
                },
                {
                    "title": "Book 2"
                }
            ]
    }}""")


@pytest.fixture
def xml_response():
    return response_with_content(b"""
    <store>
      <book author="author 1"><title>Book 1</title></book>
      <book author="author 2"><title>Book 2</title></book>
    </store>
    """)


@pytest.fixture
def xhtml_response():
    return response_with_content(b"""
    <?xml version="1.0" encoding="UTF-8"?>
      <?xml-stylesheet href="xhtml-default.css" type="text/css" media="screen, aural, print" ?>
      <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
       "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
      <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en" dir="ltr">
        <head lang="en" xml:lang="en" dir="ltr" profile="profile">
        </head>
        <body id="body" class="body" title="body" lang="en" xml:lang="en" dir="ltr">
          <h1 id="title" class="title" title="document title" lang="en"
            xml:lang="en" dir="ltr">Sample XHTML 1.0 document</h1>
        </body>
      </html>
    """)


def rest_requests():
    return (
        (
            'GET http://example.org',  # value
            RESTRequest('GET', 'http://example.org', {}, '')  # expected
        ),
        (
            'POST http://example.org',
            RESTRequest('POST', 'http://example.org', {}, '')
        ),
        (
            'get http://example1.org\n\n',
            RESTRequest('GET', 'http://example1.org', {}, '')
        ),
        (
            'http://example.org',
            RESTRequest('', 'http://example.org', {}, '')
        ),
        (
            '  \n\n\tgeT http://example.org:8000'
            '/lib/some.php/?var=1&var=2#test\n',
            RESTRequest('GET',
                        'http://example.org:8000'
                        '/lib/some.php/?var=1&var=2#test',
                        {},
                        '')
        ),
        (
            'GET http://example.org\nContent-Type: application/json',
            RESTRequest('GET',
                        'http://example.org',
                        {'Content-Type': 'application/json'},
                        '')
        ),
        (
            """GET http://example.org
            Content-Type  : application/json
            Authorization: Basic xYz
            """,
            RESTRequest('GET',
                        'http://example.org',
                        {
                            'Content-Type': 'application/json',
                            'Authorization': 'Basic xYz',
                        },
                        '')
        ),
        (
            'GET http://example.org\n'
            'Content-Type  : application/json\n'
            'Authorization: Basic xYz\n'
            '\n'
            'Body:text\nmultiline',
            RESTRequest('GET',
                        'http://example.org',
                        {
                            'Content-Type': 'application/json',
                            'Authorization': 'Basic xYz',
                        },
                        'Body:text\nmultiline')
        ),
        (
            'GET http://example.org\n\nBody:text',
            RESTRequest('GET', 'http://example.org', {}, 'Body:text')
        ),
        (
            'GET http://example.org\n \t   \nBody:text',
            RESTRequest('GET', 'http://example.org', {}, 'Body:text')
        ),
        (
            'GET http://example.org HTTP/1.1',
            RESTRequest('GET', 'http://example.org', {}, '')
        ),
    )


@pytest.mark.parametrize(
    'value', [
        'GET example.org example.org',
        'Content-Type: application/json',
        '\n\n',
        '',
    ]
)
def test_exception_on_inalid_request(value):
    with pytest.raises(ParseError):
        parse_rest_request(value)


@pytest.mark.parametrize(
    'value, expected',
    rest_requests()
)
def test_request_method_parsed(value, expected):
    assert parse_rest_request(value).method == expected.method


@pytest.mark.parametrize(
    'value, expected',
    rest_requests()
)
def test_request_url_parsed(value, expected):
    assert parse_rest_request(value).url == expected.url


@pytest.mark.parametrize(
    'value, expected',
    rest_requests()
)
def test_request_headers_parsed(value, expected):
    assert parse_rest_request(value).headers == expected.headers


@pytest.mark.parametrize(
    'value, expected',
    rest_requests()
)
def test_request_body_parsed(value, expected):
    assert parse_rest_request(value).body == expected.body


@pytest.mark.parametrize(
    'text, kwargs, expected',
    (
        ('', {}, ''),
        ('\n', {}, '\n'),
        ('$', {}, '$'),
        ('$$', {}, '$'),
        ('$$', {}, '$'),
        ('{', {}, '{'),
        ('}', {}, '}'),
        ('{}', {}, '{}'),
        ('{\n}', {}, '{\n}'),
        ('${}', {}, '${}'),
        ('$_$', {}, '$_$'),
        ('$_$', {'_': 100}, '100$'),
        ('{"user": "$user"}', {'user': 'test'}, '{"user": "test"}'),
        ('{"user": "${user}"}', {'user': 'test'}, '{"user": "test"}'),
        ('POST $root/json\nHeader: $header\n\n{\n"user": "${user}"\n}',
         {
             'root': 'https://httpbin.org',
             'header': 'value',
             'user': 'test',
         },
         'POST https://httpbin.org/json\nHeader: value\n\n'
         '{\n"user": "test"\n}')
    )
)
def test_variables_expanded(text, kwargs, expected):
    assert expand_variables(text, kwargs) == expected


@pytest.mark.parametrize(
    'expression, expected', (
        ('store.book.[1].title', {'store.book.[1].title': 'Book 2'}),
        ('.store.book.[1].title', {'store.book.[1].title': 'Book 2'}),
        ('$..title', {'store.book.[0].title': 'Book 1', 'store.book.[1].title': 'Book 2'}),
        ('..title', {'store.book.[0].title': 'Book 1', 'store.book.[1].title': 'Book 2'}),
        ('nosuchitem', {}),
        ('$', {'$': {'store': {'book': [{'title': 'Book 1'}, {'title': 'Book 2'}]}}}),
        ('', {'$': {'store': {'book': [{'title': 'Book 1'}, {'title': 'Book 2'}]}}}),
    )
)
def test_json_response_parsed(json_response, expression, expected):
    assert parse_json_response(response=json_response, expression=expression) == expected


@pytest.mark.parametrize(
    'expression, expected', (
        ('/store/book[2]/title', {'/store/book[2]/title': '<title>Book 2</title>\n'}),
        ('/store/book[2]/title/text()', {'/store/book[2]/title': 'Book 2'}),
        ('/store/book[2]/@author',  {'/store/book[2]': 'author 2'}),
        ('//@author',  {'/store/book[1]': 'author 1', '/store/book[2]': 'author 2'}),
        ('count(//book)', {'count(//book)': 2.0}),
        ('boolean(//book)', {'boolean(//book)': True}),
        ('count(//book) > 10', {'count(//book) > 10': False}),
        ('string("test")', {'string("test")': 'test'}),
        ('concat(//store/book[1]/title, " by ", //store/book[1]/@author)', {
            'concat(//store/book[1]/title, " by ", //store/book[1]/@author)': 'Book 1 by author 1'
        }),
        ('//nosuchitem', {}),
    )
)
def test_xml_response_parsed(xml_response, expression, expected):
    assert XPathParser('xml')(response=xml_response, expression=expression) == expected


def test_xhtml_response_parsed(xhtml_response,):
    assert XPathParser('html')(response=xhtml_response, expression='//h1/@title') == {
        '/html/body/h1': 'document title'
    }


@pytest.mark.parametrize('subtype', ('json', 'xml', 'html'))
def test_response_parser_known_subtype(json_response, subtype):
    parser = ResponseParser(response=json_response, expression=None, content_subtype=subtype)
    assert parser.parser


@pytest.mark.parametrize('subtype', ('text', None))
def test_response_parser_unknown_subtype(json_response, subtype):
    with pytest.raises(UnknownSubtype):
        ResponseParser(response=response_with_content(b''), expression=None,
                       content_subtype=subtype)


@pytest.mark.parametrize(
    'text, expected', (
        ('', ''),
        ('test', 'test'),
        ('"test test"', 'test test'),
        ("'test test'", 'test test'),
        ("'test' 'test' \"test\"", "test 'test' \"test\""),
        ("test 'test'", "test 'test'"),
    )
)
def test_quotes_removed_from_argument(text, expected):
    remove_argument_quotes(text) == expected
