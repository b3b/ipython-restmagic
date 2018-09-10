"""restmagic.magic"""
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

    @line_magic('rest')
    @cell_magic('rest')
    def rest(self, line, cell=''):
        """Run given HTTP query."""
        rest_request = parse_rest_request('\n'.join((
            line,
            expand_variables(cell, self.get_user_namespace())
        )))
        sender = RequestSender()
        response = sender.send(rest_request)
        print(sender.dump())
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


def load_ipython_extension(ipython):
    """Hook for `%load_extension restmagic` IPython command."""
    ipython.register_magics(RESTMagic)
