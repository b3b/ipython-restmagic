from __future__ import unicode_literals
import pytest

from restmagic.display import display_response, get_mime_type


@pytest.fixture
def set_mime_type(mocker):
    def _set_mime_type(mime_type):
        return mocker.patch('restmagic.display.get_mime_type',
                            return_value=mime_type)
    return _set_mime_type


@pytest.fixture
def response(mocker):
    def _response(headers=None, text='', content=b'', json=None):
        r = mocker.Mock()
        r.headers = headers or {}
        r.content = content
        r.text = text
        r.json = lambda: json or {}
        return r
    return _response


@pytest.fixture
def ipython_display(mocker):
    return mocker.patch('restmagic.display.display')


@pytest.mark.parametrize(
    'headers, expected', (
        ({}, None),
        ({'content-type': 'application/json'}, 'application/json'),
        ({'content-type': 'text/html; charset=utf-8'}, 'text/html'),
    ))
def test_mime_type_detected(mocker, headers, expected):
    response = mocker.Mock()
    response.headers = headers
    assert get_mime_type(response) == expected


def test_display_json_response(set_mime_type, response):
    set_mime_type('application/json')
    display_response(response(json={'a': 123, 'b': 4}))


@pytest.mark.parametrize('mime_type', (
    'application/json',
    'unknown',
    None
    ))
def test_ipython_display_called(mime_type, set_mime_type, ipython_display,
                                response):
    set_mime_type(mime_type)
    display_response(response())
    ipython_display.assert_called_once()
