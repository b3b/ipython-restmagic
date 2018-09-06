"""restmagic.magic"""
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

from restmagic.parser import parse_rest_request
from restmagic.sender import RequestSender


@magics_class
class RESTMagic(Magics):
    """Provides the %%rest magic."""

    @line_magic('rest')
    @cell_magic('rest')
    def rest(self, line, cell=''):
        """Run given HTTP query."""
        rest_request = parse_rest_request('\n'.join((line, cell)))
        sender = RequestSender()
        response = sender.send(rest_request)
        print(sender.dump())
        return response


def load_ipython_extension(ipython):
    """Hook for `%load_extension restmagic` IPython command."""
    ipython.register_magics(RESTMagic)
