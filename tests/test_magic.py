from argparse import Namespace
from unittest import mock

import pytest
from requests.exceptions import SSLError
from IPython import get_ipython

from restmagic.magic import RESTMagic
from restmagic.parser import ParseError, UnknownSubtype
from restmagic.request import RESTRequest


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
    return mocker.patch('restmagic.magic.parse_rest_request',
                        return_value=RESTRequest())


@pytest.fixture(autouse=True)
def display_dict(mocker):
    return mocker.patch('restmagic.magic.display_dict', return_value=None)


@pytest.fixture(autouse=True)
def display_response(mocker):
    return mocker.patch('restmagic.magic.display_response', return_value=None)


@pytest.fixture
def response_parser(mocker):
    return mocker.patch('restmagic.magic.ResponseParser')


@pytest.fixture(autouse=True)
def display_usage_example(mocker):
    return mocker.patch('restmagic.magic.display_usage_example')


@pytest.fixture(autouse=True)
def showtraceback(mocker):
    return mocker.patch('IPython.core.interactiveshell.'
                        'InteractiveShell.showtraceback')


def test_send_response_returned_by_rest_command(send):
    result = RESTMagic().rest('GET http://localhost')
    send.assert_called_once()
    assert result == 'test sended'


def test_root_values_are_added_to_query(parse_rest_request, send):
    rest = RESTMagic()
    rest.root = RESTRequest(method='POST', url='http://example.org')
    parse_rest_request.return_value = RESTRequest(url='test')
    rest.rest('GET test')
    args = send.call_args[0]
    assert args[0] == RESTRequest(method='POST', url='http://example.org/test')


def test_default_method_and_scheme_added_to_query(parse_rest_request, send):
    rest = RESTMagic()
    parse_rest_request.return_value = RESTRequest(url='test')
    rest.rest('test')
    args = send.call_args[0]
    assert args[0] == RESTRequest(method='GET', url='https://test')


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


def test_traceback_is_shown_if_display_fail(ip, display_response,
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


def test_no_display_in_quiet_mode(display_response):
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


def test_root_is_set(ip, parse_rest_request):
    rest = ip.find_magic('rest').__self__
    parse_rest_request.return_value = RESTRequest(url='test')
    assert rest.root is None
    ip.run_line_magic('rest_root', 'test')
    assert rest.root == RESTRequest(url='test')


def test_root_is_canceled(ip):
    rest = ip.find_magic('rest').__self__
    rest.root = RESTRequest(url='test')
    ip.run_line_magic('rest_root', '')
    assert rest.root is None


def test_root_args_saved(ip):
    rest = ip.find_magic('rest').__self__
    assert 'verbose' not in vars(rest.root_args)
    ip.run_line_magic('rest_root', '-v')
    assert rest.root_args.verbose is True


def test_root_args_canceled(ip):
    rest = ip.find_magic('rest').__self__
    rest.root_args = Namespace(verbose=True)
    assert rest.root_args != Namespace()
    ip.run_line_magic('rest_root', '')
    assert rest.root_args == Namespace()


def test_send_exception_is_reported(ip, send):
    send.side_effect = Exception('test')
    result = ip.run_line_magic('rest_root', '')
    assert result is None
    assert ip.showtraceback.called_once()


def test_usage_displayed_on_parse_error(parse_rest_request,
                                        display_usage_example):
    parse_rest_request.side_effect = ParseError('test')
    result = RESTMagic().rest('')
    assert result is None
    display_usage_example.assert_called_once()


def test_insecure_option_hint_shown_on_ssl_cert_error(capsys, ip, send):
    send.side_effect = SSLError()
    result = ip.run_line_magic('rest', '')
    assert result is None
    assert ip.showtraceback.called_once()
    err = capsys.readouterr()[1]
    assert 'Use `%rest --insecure`' in err


@pytest.mark.parametrize(
    'root_args, args, expected', (
        (Namespace(), Namespace(), False),
        (Namespace(), Namespace(verbose=True), True),
        (Namespace(verbose=True), Namespace(), True),
        (Namespace(verbose=None), Namespace(), False),
        (Namespace(verbose=True), Namespace(verbose=None), True),
    ))
def test_args_combined(root_args, args, expected):
    rest = RESTMagic()
    rest.root_args = root_args
    assert rest.get_args(args).verbose == expected


def test_insecure_option_handled(send):
    RESTMagic().rest(line='-k GET http://localhost')
    assert send.call_args[1]['verify'] is False


def test_proxy_option_handled(send):
    RESTMagic().rest(line='--proxy 127.0.0.1:9000 GET http://localhost')
    assert send.call_args[1]['proxy'] == '127.0.0.1:9000'


def test_max_redirects_option_handled(send):
    RESTMagic().rest(line='GET http://localhost')
    assert send.call_args[1]['max_redirects'] == 30

    RESTMagic().rest(line='--max-redirects 0 GET http://localhost')
    assert send.call_args[1]['max_redirects'] == 0


def test_timeout_option_handled(send):
    RESTMagic().rest(line='GET http://localhost')
    assert send.call_args[1]['timeout'] == 10

    RESTMagic().rest(line='--timeout 1.01 GET http://localhost')
    assert send.call_args[1]['timeout'] == 1.01


@pytest.mark.parametrize('option', ('-[', '--extract'))
def test_extract_option_handled(send, display_dict, display_response,
                                response_parser, option):
    RESTMagic().rest(line=f"{option} test GET http://localhost")
    response_parser.assert_called_once_with(response='test sended', expression='test',
                                            content_subtype=None)
    display_dict.assert_called_once()


@pytest.mark.parametrize(
    'line, expected_expression', (
        ('-[ "a b"', 'a b'),
        ('--extract \'/[name() = "svg"]\'', '/[name() = "svg"]'),
    )
)
def test_extract_option_quoted_expression_handled(send, display_dict, display_response,
                                                  response_parser, line, expected_expression):
    RESTMagic().rest(line=f"{line} test GET http://localhost")
    response_parser.assert_called_once_with(response='test sended', expression=expected_expression,
                                            content_subtype=None)
    display_dict.assert_called_once()


@pytest.mark.parametrize('parser', ('json', 'xml', 'html'))
def test_parser_option_handled(send, display_dict, display_response,
                               response_parser, parser):
    RESTMagic().rest(line=f"--parser {parser} -[ test GET http://localhost")
    response_parser.assert_called_once_with(response=mock.ANY, expression=mock.ANY,
                                            content_subtype=parser)


def test_traceback_is_shown_if_parse_reponse_fail(ip, response_parser, showtraceback):
    response_parser.side_effect = Exception()
    result = ip.run_cell_magic('rest', '-[ $.*', 'GET /')
    showtraceback.assert_called_once()
    assert response_parser.call_count == 1
    assert result == 'test sended'


def test_parser_option_hint_shown_on_unknown_subtype(capsys, ip, response_parser, showtraceback):
    response_parser.side_effect = UnknownSubtype('...')
    ip.run_cell_magic('rest', '-[ $.*', 'GET /')
    showtraceback.assert_called_once()
    err = capsys.readouterr()[1]
    assert 'Use `%rest --parser`' in err
