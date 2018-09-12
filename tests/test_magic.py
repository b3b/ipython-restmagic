import pytest
from restmagic.magic import RESTMagic
from IPython import get_ipython


@pytest.fixture
def ip():
    ip = get_ipython()
    ip.register_magics(RESTMagic)
    ip.user_global_ns['test_var'] = 'test value'
    yield ip
    ip.user_global_ns.pop('test_var', None)
    ip.user_global_ns.pop('_restmagic_session', None)


@pytest.fixture(autouse=True)
def send(mocker):
    return mocker.patch('restmagic.magic.RequestSender.send',
                        return_value='test sended')


@pytest.fixture(autouse=True)
def close_session(mocker):
    return mocker.patch('restmagic.magic.RequestSender.close_session')


@pytest.fixture(autouse=True)
def dump(mocker):
    return mocker.patch('restmagic.magic.RequestSender.dump',
                        return_value='session dump')


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


def test_command_options_extracted_from_query(parse_rest_request):
    RESTMagic().rest(line='-v -v -v GET http://localhost')
    parse_rest_request.assert_called_once_with('GET http://localhost\n')


def test_session_dumped_in_verbose_mode(dump):
    RESTMagic().rest(line='-v GET http://localhost')
    dump.assert_called_once()


def test_no_display_in_quit_mode(display_response):
    RESTMagic().rest(line='-q GET http://localhost')
    display_response.assert_not_called()


def test_sender_not_reused(ip):
    rest = ip.find_magic('rest').__self__
    assert rest.sender is None

    ip.run_line_magic('rest', 'GET /')
    assert rest.sender is None


def test_sender_reused_for_persistent_session(ip):
    rest = ip.find_magic('rest').__self__
    assert rest.sender is None

    ip.run_line_magic('rest_session', '')
    assert rest.sender is not None
    assert rest.sender.send.call_count == 0
    sender = rest.sender

    ip.run_line_magic('rest', 'GET /')
    assert rest.sender == sender
    assert sender.send.call_count == 1

    ip.run_line_magic('rest', 'GET /')
    assert rest.sender == sender
    assert sender.send.call_count == 2


def test_rest_session_ended(ip):
    rest = ip.find_magic('rest').__self__
    ip.run_line_magic('rest_session', '')
    sender = rest.sender

    ip.run_line_magic('rest_session', '-e')
    assert rest.sender is None
    sender.close_session.assert_called_once()


def test_rest_session_recreated(ip):
    rest = ip.find_magic('rest').__self__
    ip.run_line_magic('rest_session', '')
    sender = rest.sender

    ip.run_line_magic('rest_session', '')
    assert rest.sender is not None
    assert rest.sender != sender
    sender.close_session.assert_called_once()
