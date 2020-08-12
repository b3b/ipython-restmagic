import pytest

from restmagic.response import get_mime_type, guess_response_content_subtype

from .utils import response_with_content


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


@pytest.mark.parametrize(
    'response, expected', [
        (response_with_content(b'', headers={'content-type': 'application/xml'}), 'xml'),
        (response_with_content(b'', headers={'content-type': 'application/json'}), 'json'),
        (response_with_content(b'', headers={'content-type': 'text/plain'}), None),
        (response_with_content(b'{}'), 'json'),
        (response_with_content(b'test'), None),
        (response_with_content(b''), None),
    ]
)
def test_guess_response_content_subtype(response, expected):
    assert guess_response_content_subtype(response) == expected
