import pytest
from restmagic.request import RESTRequest


@pytest.mark.parametrize(
    'a, b, expected', (
        (RESTRequest(), RESTRequest(), RESTRequest()),
        (RESTRequest(method='POST'), RESTRequest(), RESTRequest('POST')),
        (RESTRequest(method=''), RESTRequest('POST'), RESTRequest('POST')),
        (RESTRequest(url='test'), RESTRequest(), RESTRequest(url='test')),
        (RESTRequest(), RESTRequest(url='api/method'),
         RESTRequest(url='api/method')),
        (RESTRequest(url='https://x'), RESTRequest(url='http://y'),
         RESTRequest(url='http://y')),
        (RESTRequest(url='/'), RESTRequest(url='/'),
         RESTRequest(url='/')),
        (RESTRequest(), RESTRequest(url='/'),
         RESTRequest(url='/')),
        (RESTRequest(url='test'), RESTRequest(url='api/method'),
         RESTRequest(url='test/api/method')),
        (RESTRequest(headers={'a': '1'}), RESTRequest(headers={}),
         RESTRequest(headers={'a': '1'})),
        (RESTRequest(headers={'a': '1', 'b': '2'}),
         RESTRequest(headers={'b': '100'}),
         RESTRequest(headers={'a': '1', 'b': '100'})),
        (RESTRequest(), RESTRequest(body='test'), RESTRequest(body='test')),
        (RESTRequest(body='test'), RESTRequest(), RESTRequest()),
    ))
def test_requests_join(a, b, expected):
    result = a + b
    assert result == expected


@pytest.mark.parametrize(
    'a, b, c, expected', (
        (RESTRequest(), RESTRequest(), RESTRequest(),
         RESTRequest()),
        (RESTRequest(), RESTRequest(), RESTRequest('PUT'),
         RESTRequest('PUT')),
        (RESTRequest('PUT'), RESTRequest(), RESTRequest(),
         RESTRequest('PUT')),
        (RESTRequest('GET', 'https://'),
         RESTRequest('PUT', 'httpbin.org'),
         RESTRequest(url='json'),
         RESTRequest('PUT', 'https://httpbin.org/json')),
    ))
def test_requests_multiple_join(a, b, c, expected):
    result = a + b + c
    assert result == expected
