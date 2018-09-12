"""restmagic.magic"""
from IPython.core import magic_arguments
from IPython.core.magic import (
    Magics,
    cell_magic,
    line_magic,
    magics_class,
)
from restmagic.display import display_response
from restmagic.parser import (
    expand_variables,
    parse_rest_request
)
from restmagic.sender import RequestSender


@magics_class
class RESTMagic(Magics):
    """Provides the %%rest magic."""

    session_varriable_name = '_restmagic_session'

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

    @line_magic('rest')
    @cell_magic('rest')
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('--verbose', '-v',
                              action='store_true',
                              help='Dump full HTTP session log.')
    @magic_arguments.argument('--quit', '-q',
                              action='store_true',
                              help='Do not print HTTP request and response.')
    @magic_arguments.argument('query', nargs='*')
    def rest(self, line, cell=''):
        """Run given HTTP query."""
        args = magic_arguments.parse_argstring(self.rest, line)
        rest_request = parse_rest_request('\n'.join((
            ' '.join(args.query),
            expand_variables(cell, self.get_user_namespace())
        )))
        sender = self.sender or RequestSender()
        response = sender.send(rest_request)
        if args.verbose and not args.quit:
            print(sender.dump())
        elif not args.quit:
            try:
                display_response(response)
            except Exception:
                print("Can't display the response.")
                self.shell.showtraceback(exception_only=True)
        return response

    def get_user_namespace(self):
        """Returns namespace to be used for variables expansion.
        """
        return getattr(self.shell, 'user_ns', {}) if self.shell else {}

    @property
    def sender(self):
        """Store class:`RequestSender` object to reuse,
        when session persistent mode is on.
        """
        return self.get_user_namespace().get(self.session_varriable_name)

    @sender.setter
    def sender(self, value):
        self.get_user_namespace()[self.session_varriable_name] = value


def load_ipython_extension(ipython):
    """Hook for `%load_extension restmagic` IPython command."""
    ipython.register_magics(RESTMagic)
