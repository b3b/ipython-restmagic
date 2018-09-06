"""restmagic.request"""


class RESTRequest():
    """Contains parsed HTTP query."""

    def __init__(self, method='', url='', headers=None, body=''):
        self.method = method
        self.url = url
        self.headers = dict(headers) if headers else {}
        self.body = body

    def __str__(self):
        return "{method} {url}".format(method=self.method, url=self.url)
