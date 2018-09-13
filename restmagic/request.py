"""restmagic.request"""
import re


class RESTRequest():
    """Contains parsed HTTP query."""

    def __init__(self, method='', url='', headers=None, body=''):
        self.method = method
        self.url = url
        self.headers = dict(headers) if headers else {}
        self.body = body

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self.__str__())

    def __str__(self):
        return "{method} {url}".format(method=self.method, url=self.url)

    def __add__(self, request):
        url = request.url
        if self.url and url and not re.match(r'^http[s]?://', url):
            url = '/'.join((
                re.sub(r'/$', '', self.url),  # root/ => root
                re.sub(r'^/', '', url)        # /path => path
            ))
        headers = self.headers.copy()
        headers.update(request.headers)

        return RESTRequest(
            method=request.method or self.method,
            url=url or self.url,
            headers=headers,
            body=request.body
        )

    def __eq__(self, request):
        return (
            self.method == request.method and
            self.url == request.url and
            self.headers == request.headers and
            self.body == request.body
        )
