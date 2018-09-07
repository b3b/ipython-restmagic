"""restmagic.sender"""
from __future__ import unicode_literals

from requests import Request, Session
from requests_toolbelt.utils.dump import dump_all


class RequestSender():
    """HTTP request sender.
    """

    def __init__(self):
        self.response = None

    def send(self, rest_request):
        """Send a given request.

        :param rest_request: :class:`RESTRequest` to send
        :rtype: requests.Response
        """
        session = Session()
        session.keep_alive = False
        req = Request(rest_request.method,
                      rest_request.url,
                      data=rest_request.body,
                      headers=rest_request.headers)
        prepared_request = session.prepare_request(req)
        self.response = session.send(prepared_request)
        return self.response

    def dump(self):
        """Dump HTTP session log.
        :rtype: str
        """
        if self.response is not None:
            # Decode errors could occur when response contains non-text data.
            # It should be OK to ignore this errors, for most cases.
            return dump_all(self.response).decode(errors='replace')
        return ''
