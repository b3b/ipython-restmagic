"""restmagic.magic"""
from __future__ import print_function

import sys

from IPython.core import magic_arguments
from IPython.core.magic import (
    Magics,
    cell_magic,
    line_magic,
    magics_class,
)
from traitlets.config.configurable import Configurable
from traitlets import Instance

from restmagic.display import display_response, display_usage_example
from restmagic.parser import (
    ParseError,
    expand_variables,
    parse_rest_request,
)
from restmagic.request import RESTRequest
from restmagic.sender import RequestSender


@magics_class
class RESTMagic(Magics, Configurable):
    """Provides the %%rest magic."""

    # Store class:`RequestSender` object to reuse,
    # when session persistent mode is on.
    sender = Instance(RequestSender, allow_none=True, config=False)
    # Store default HTTP query values.
    root = Instance(RESTRequest, allow_none=True, config=False)

    @line_magic('rest_session')
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('--end', '-e',
                              action='store_true',
                              help=('End the current the session,'
                                    ' and do not start a new one.'))
    def rest_session(self, line):
        """Start persistent HTTP session.
        """
        args = magic_arguments.parse_argstring(self.rest_session, line)
        sender = self.sender
        if sender:
            sender.close_session()
            print('Session ended.')

        if args.end:
            self.sender = None
        else:
            self.sender = RequestSender(keep_alive=True)
            print('New session started.')

    @line_magic('rest_root')
    @cell_magic('rest_root')
    def rest_root(self, line, cell=''):
        """Set default HTTP query values, to be used by all subsequent queries.
        """
        if line or cell:
            try:
                self.root = parse_rest_request('\n'.join((
                    line,
                    expand_variables(cell, self.get_user_namespace())
                )))
            except ParseError as ex:
                display_usage_example(magic='rest_root', error_text=str(ex),
                                      is_cell_magic=(cell != ''))
                return
            else:
                print('Requests defaults are set.')
        else:
            self.root = None
            print('Requests defaults are canceled.')

    @line_magic('rest')
    @cell_magic('rest')
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('--verbose', '-v',
                              action='store_true',
                              help='Dump full HTTP session log.')
    @magic_arguments.argument('--quiet', '-q',
                              action='store_true',
                              help='Do not print HTTP request and response.')
    @magic_arguments.argument('query', nargs='*')
    def rest(self, line, cell=''):
        """Run given HTTP query."""
        args = magic_arguments.parse_argstring(self.rest, line)
        try:
            rest_request = parse_rest_request('\n'.join((
                ' '.join(args.query),
                expand_variables(cell, self.get_user_namespace())
            )))
        except ParseError as ex:
            display_usage_example(magic='rest', error_text=str(ex),
                                  is_cell_magic=(cell != ''))
            return None

        sender = self.sender or RequestSender()
        root = self.root or RESTRequest()

        try:
            response = sender.send(
                RESTRequest('GET', 'https://') + root + rest_request
            )
        except Exception:
            print("Request was not completed.", file=sys.stderr)
            self.shell.showtraceback(exception_only=True)
            return None

        if args.verbose and not args.quiet:
            print(sender.dump())
        elif not args.quiet:
            try:
                display_response(response)
            except Exception:
                print("Can't display the response.", file=sys.stderr)
                self.shell.showtraceback(exception_only=True)
        return response

    def get_user_namespace(self):
        """Returns namespace to be used for variables expansion.
        """
        return getattr(self.shell, 'user_ns', {}) if self.shell else {}


def load_ipython_extension(ipython):
    """Hook for `%load_extension restmagic` IPython command."""
    ipython.register_magics(RESTMagic)
