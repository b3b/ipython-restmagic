import pytest
from restmagic.magic import RESTMagic
from IPython import get_ipython


@pytest.fixture
def ip():
    ip = get_ipython()
    ip.register_magics(RESTMagic)
    ip.user_global_ns['test_var'] = 'test value'
    return ip


@pytest.fixture(autouse=True)
def send(mocker):
    return mocker.patch('restmagic.magic.RequestSender.send',
                        return_value='test sended')


@pytest.fixture(autouse=True)
def expand_variables(mocker):
    return mocker.patch('restmagic.magic.expand_variables', return_value='')


@pytest.fixture(autouse=True)
def parse_rest_request(mocker):
    return mocker.patch('restmagic.magic.parse_rest_request', return_value='')


@pytest.fixture(autouse=True)
def display_response(mocker):
    return mocker.patch('restmagic.magic.display_response', return_value=None)


@pytest.fixture(autouse=True)
def showtraceback(mocker):
    return mocker.patch('IPython.core.interactiveshell.'
                        'InteractiveShell.showtraceback')


def test_send_response_returned_by_rest_command(send):
    result = RESTMagic().rest('GET http://localhost')
    send.assert_called_once()
    assert result == 'test sended'


def test_variables_expansion_used_by_rest_command(mocker, expand_variables):
    mocker.patch('restmagic.magic.RESTMagic.get_user_namespace',
                 return_value={'ct': 'application/json'})
    RESTMagic().rest(line='GET http://localhost', cell='Content-Type: $ct')
    # line variables are already expanded by IPython,
    # expand_variables() should be called only for cell text
    expand_variables.assert_called_once_with(
        'Content-Type: $ct',
        {'ct': 'application/json'}
    )


def test_user_variables_are_passed_to_expand_variables(ip, expand_variables):
    ip.run_cell_magic('rest', '', 'GET /')
    kwargs = expand_variables.call_args[0][1]
    assert kwargs['test_var'] == 'test value'


def test_traceback_is_shown_if_display_fail(ip, mocker, display_response,
                                            showtraceback):
    display_response.side_effect = Exception()
    result = ip.run_cell_magic('rest', '', 'GET /')
    showtraceback.assert_called_once()
    assert result == 'test sended'
