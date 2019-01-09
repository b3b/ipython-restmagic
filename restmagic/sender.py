"""restmagic.sender"""
from __future__ import print_function, unicode_literals

import warnings

from requests import Request, Session
from requests_toolbelt.utils.dump import dump_all
from urllib3.exceptions import InsecureRequestWarning


class RequestSender():
    """HTTP request sender.

    :param keep_alive: use persistent connection
    """

    def __init__(self, keep_alive=False):
        self.session = None
        self.response = None
        self.keep_alive = keep_alive

    def send(self, rest_request, verify=True, proxy=None):
        """Send a given request.

        :param rest_request: :class:`RESTRequest` to send
        :rtype: requests.Response
        """
        session = self.get_session()
        req = Request(rest_request.method,
                      rest_request.url,
                      data=rest_request.body.encode('utf-8'),
                      headers=rest_request.headers)
        prepared_request = session.prepare_request(req)
        if proxy:
            proxies = {
                'http': proxy,
                'https': proxy
            }
        else:
            proxies = {}
        with warnings.catch_warnings():
            # suppress "Unverified HTTPS request is being made" warning
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)
            self.response = session.send(
                prepared_request,
                verify=verify,
                proxies=proxies,
            )
        return self.response

    def get_session(self):
        """Returns the current session.
        """
        if self.keep_alive:
            if not self.session:
                self.session = Session()
            session = self.session
        else:
            session = Session()
            session.keep_alive = self.keep_alive
        return session

    def close_session(self):
        """Close the current session.
        """
        if self.session:
            self.session.close()
            self.session = None

    def dump(self):
        """Dump HTTP session log.
        :rtype: str
        """
        if self.response is not None:
            # Decode errors could occur when response contains non-text data.
            # It should be OK to ignore this errors, for most cases.
            return dump_all(self.response).decode(errors='replace')
        return ''
