import re

from webserver.http_message import HttpMessage

REQUEST_REGEX = re.compile(r'(?P<method>GET|PUT|POST|HEAD|OPTIONS|DELETE) '
                           r'(?P<path>/[^\s]*) '
                           r'(?P<version>HTTP/\d\.\d)')


class Request(HttpMessage):
    def __init__(self, method: str = 'GET',
                 path: str = '/',
                 version='HTTP/1.1',
                 line: str = '',
                 headers: dict = None,
                 body: bytes = b''):
        self.method = method
        self.path = path
        self.version = version
        super().__init__(line, headers, body)

    @property
    def line(self):
        return f'{self.method} {self.path} {self.version}'

    @line.setter
    def line(self, line):
        self._line = line
        if match := REQUEST_REGEX.match(line):
            self.method, self.path, self.version = match.groups()
