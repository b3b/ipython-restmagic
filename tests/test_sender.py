import re

import pytest
import requests
import responses

from restmagic import RESTRequest
from restmagic.sender import RequestSender


@pytest.fixture
@responses.activate
def successful_response():
    responses.add(responses.GET, re.compile('.*'))
    return requests.get('http://localhost/test',
                        headers={'Test-Header': '111'})


@pytest.fixture
@responses.activate
def unsuccessful_response():
    responses.add(responses.GET, re.compile('.*'), status=401)
    return requests.get('http://localhost/test',
                        headers={'Test-Header': '111'})


@pytest.fixture
def requests_send(mocker):
    return mocker.patch('restmagic.sender.Session.send',
                        return_value='test sended')


@responses.activate
def test_request_sended():
    responses.add(responses.GET, re.compile('.*'))
    assert len(responses.calls) == 0
    RequestSender().send(RESTRequest('GET', 'http://localhost/test1'))
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://localhost/test1'


def test_request_parts_sended(requests_send):
    sender = RequestSender()
    assert sender.response is None
    rest_request = RESTRequest('POST', 'http://localhost/test',
                               headers={'Test-Header': '1234'},
                               body='{"test": "value"}')
    sender.send(rest_request)
    prepared_request = requests_send.call_args[0][0]
    assert prepared_request.method == 'POST'
    assert prepared_request.url == 'http://localhost/test'
    assert prepared_request.headers['Test-Header'] == '1234'
    assert prepared_request.body == b'{"test": "value"}'


def test_response_saved_by_send(requests_send):
    sender = RequestSender()
    assert sender.response is None
    sender.send(RESTRequest('GET', 'http://localhost/test'))
    assert sender.response == 'test sended'


def test_method_url_in_dump(successful_response):
    sender = RequestSender()
    sender.response = successful_response
    assert 'GET /test' in sender.dump()


def test_request_headers_in_dump(successful_response):
    sender = RequestSender()
    sender.response = successful_response
    assert 'Test-Header: 111' in sender.dump()


def test_response_status_in_dump(successful_response):
    sender = RequestSender()
    sender.response = successful_response
    assert '200 OK' in sender.dump()


def test_method_url_in_unsuccessful_dump(unsuccessful_response):
    sender = RequestSender()
    sender.response = unsuccessful_response
    assert 'GET /test' in sender.dump()


def test_session_not_reused(requests_send):
    sender = RequestSender()
    sender.send(RESTRequest('GET', 'http://localhost/test'))
    assert not sender.session


def test_persistent_session_reused(requests_send):
    sender = RequestSender(keep_alive=True)

    sender.send(RESTRequest('GET', 'http://localhost/test'))
    session = sender.session
    assert session
    assert getattr(session, 'keep_alive', True)

    sender.send(RESTRequest('GET', 'http://localhost/test'))
    assert sender.session == session


def test_body_sended_as_bytes(requests_send):
    sender = RequestSender()
    sender.send(RESTRequest('POST', 'https://httpbin.org/post',
                            body='{"\u03C0": "\u03C0"}'))
    prepared_request = requests_send.call_args[0][0]
    assert isinstance(prepared_request.body, bytes)


def test_verify_option_enabled(requests_send):
    sender = RequestSender()

    sender.send(RESTRequest('GET', 'http://localhost/test'))
    assert requests_send.call_args[1]['verify'] is True

    sender.send(RESTRequest('GET', 'http://localhost/test'), verify=False)
    assert requests_send.call_args[1]['verify'] is False


def test_cacert_added(requests_send):
    sender = RequestSender()

    sender.send(RESTRequest('GET', 'http://localhost/test'), cacert='test.pem')
    assert requests_send.call_args[1]['verify'] == 'test.pem'


def test_proxy_option_enabled(requests_send):
    sender = RequestSender()

    sender.send(RESTRequest('GET', 'http://localhost/test'))
    assert requests_send.call_args[1]['proxies'] == {}

    sender.send(RESTRequest('GET', 'http://localhost/test'),
                proxy='127.0.0.1:9000')
    assert requests_send.call_args[1]['proxies'] == {
        'http': '127.0.0.1:9000',
        'https': '127.0.0.1:9000'
    }


def test_max_redirects_option_enabled(mocker, requests_send):
    sender = RequestSender()
    session = requests.Session()
    mocker.patch('restmagic.sender.RequestSender.get_session',
                 return_value=session)

    sender.send(RESTRequest('GET', 'http://localhost/test'))
    assert session.max_redirects is None

    sender.send(RESTRequest('GET', 'http://localhost/test'),
                max_redirects=3)
    assert session.max_redirects == 3


def test_timeout_option_enabled(mocker, requests_send):
    sender = RequestSender()

    sender.send(RESTRequest('GET', 'http://localhost/test'))
    assert requests_send.call_args[1]['timeout'] is None

    sender.send(RESTRequest('GET', 'http://localhost/test'),
                timeout=0.01)
    assert requests_send.call_args[1]['timeout'] == 0.01


@pytest.mark.parametrize(
    'cert, key, expected_cert', (
        (None, None, (None, None)),
        ('cert.pem', None, ('cert.pem', None)),
        (None, 'key.pem', (None, 'key.pem')),
        ('cert.pem', 'key.pem', ('cert.pem', 'key.pem')),
    )
)
def test_cert_and_key_added(mocker, requests_send, cert, key, expected_cert):
    sender = RequestSender()

    sender.send(RESTRequest('GET', 'http://localhost/test'),
                cert=cert, key=key)

    assert requests_send.call_args[1]['cert'] == expected_cert
