import mock
from restmagic.magic import RESTMagic


@mock.patch('restmagic.magic.RequestSender.send', return_value='test sended')
def test_send_response_returned_by_rest_command(send):
    assert RESTMagic().rest('GET http://localhost') == 'test sended'
