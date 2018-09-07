import re

import pytest
import requests
import responses

import mock
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


@responses.activate
def test_request_sended():
    responses.add(responses.GET, re.compile('.*'))
    assert len(responses.calls) == 0
    RequestSender().send(RESTRequest('GET', 'http://localhost/test1'))
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://localhost/test1'


@mock.patch('restmagic.sender.Session.send')
def test_request_parts_sended(send):
    sender = RequestSender()
    assert sender.response is None
    sender.send(RESTRequest('POST', 'http://localhost/test',
                            headers={'Test-Header': '1234'},
                            body='{"test": "value"}'
    ))
    prepared_request = send.call_args[0][0]
    assert prepared_request.method == 'POST'
    assert prepared_request.url == 'http://localhost/test'
    assert prepared_request.headers['Test-Header'] == '1234'
    assert prepared_request.body == '{"test": "value"}'


@mock.patch('restmagic.sender.Session.send', return_value='test sended')
def test_response_saved_by_send(send):
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
