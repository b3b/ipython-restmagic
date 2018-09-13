import pytest

from restmagic.parser import (
    ParseError,
    RESTRequest,
    expand_variables,
    parse_rest_request,
)


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
