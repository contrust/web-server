import re

HTTP_MESSAGE_REGEX = re.compile(
    rb'(?P<line>([^\s]+)\s([^\s]+)\s(.*?))\r\n'
    rb'(?P<headers>(?:.*?: .*?\r\n)*)\r\n'
    rb'(?P<body>.*)', re.DOTALL)
REQUEST_REGEX = re.compile(r'(?P<method>GET|PUT|POST|HEAD|OPTIONS|DELETE) '
                           r'(?P<path>/[^\s]*) '
                           r'(?P<version>HTTP/\d\.\d)')
RESPONSE_REGEX = re.compile(r'(?P<version>HTTP/\d\.\d) '
                            r'(?P<code>\d{3}) '
                            r'(?P<code_description>.*)')
CODES_DESCRIPTION = {
    100: ('Continue', 'Request received, please continue'),
    101: ('Switching Protocols',
          'Switching to new protocol; obey Upgrade header'),

    200: ('OK', 'Request fulfilled, document follows'),
    201: ('Created', 'Document created, URL follows'),
    202: ('Accepted',
          'Request accepted, processing continues off-line'),
    203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
    204: ('No Content', 'Request fulfilled, nothing follows'),
    205: ('Reset Content', 'Clear input form for further input.'),
    206: ('Partial Content', 'Partial content follows.'),

    300: ('Multiple Choices',
          'Object has several resources -- see URI list'),
    301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
    302: ('Found', 'Object moved temporarily -- see URI list'),
    303: ('See Other', 'Object moved -- see Method and URL list'),
    304: ('Not Modified',
          'Document has not changed since given time'),
    305: ('Use Proxy',
          'You must use proxy specified in Location to access this '
          'resource.'),
    307: ('Temporary Redirect',
          'Object moved temporarily -- see URI list'),

    400: ('Bad Request',
          'Bad request syntax or unsupported method'),
    401: ('Unauthorized',
          'No permission -- see authorization schemes'),
    402: ('Payment Required',
          'No payment -- see charging schemes'),
    403: ('Forbidden',
          'Request forbidden -- authorization will not help'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed',
          'Specified method is invalid for this server.'),
    406: ('Not Acceptable', 'URI not available in preferred format.'),
    407: ('Proxy Authentication Required', 'You must authenticate with '
                                           'this proxy before proceeding.'),
    408: ('Request Timeout', 'Request timed out; try again later.'),
    409: ('Conflict', 'Request conflict.'),
    410: ('Gone',
          'URI no longer exists and has been permanently removed.'),
    411: ('Length Required', 'Client must specify Content-Length.'),
    412: ('Precondition Failed', 'Precondition in headers is false.'),
    413: ('Request Entity Too Large', 'Entity is too large.'),
    414: ('Request-URI Too Long', 'URI is too long.'),
    415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
    416: ('Requested Range Not Satisfiable',
          'Cannot satisfy request range.'),
    417: ('Expectation Failed',
          'Expect condition could not be satisfied.'),

    500: ('Internal Server Error', 'Server got itself in trouble'),
    501: ('Not Implemented',
          'Server does not support this operation'),
    502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
    503: ('Service Unavailable',
          'The server cannot process the request due to a high load'),
    504: ('Gateway Timeout',
          'The gateway server did not receive a timely response'),
    505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
}
HOST_REGEX = re.compile(
    r'(?P<hostname>[^:]+)(:(?P<port>\d{1,5}))?')


class HttpMessage:
    """
    HTTP message with parameters.
    """
    def __init__(self,
                 line: str = '',
                 headers: dict = None,
                 body: bytes = b''):
        self.line = line
        self.headers = headers if headers else {}
        self.body = body

    def parse(self, message: bytes):
        """
        Get instance of parsed http message.
        """
        match = HTTP_MESSAGE_REGEX.match(message)
        if match:
            self.line = match.group('line').decode('utf-8')
            if match.group('headers'):
                self.headers = dict(map(lambda x: x.split(': ', maxsplit=1),
                                        match.group('headers')
                                        .decode('utf-8')
                                        .splitlines()))
            if match.group('body'):
                self.body = match.group('body')
            return self
        raise ValueError

    @property
    def host(self) -> tuple:
        """
        Get tuple with hostname and port.
        """
        match = HOST_REGEX.match(self.headers.get('Host', ' '))
        hostname = match.group('hostname')
        port = int(port) if (port := match.group('port')) else 80
        return tuple([hostname, port])

    def __bytes__(self) -> bytes:
        """
        Get byte representation.
        """
        return (self.line.encode('utf-8') + b'\r\n' +
                b''.join(map(lambda x: f'{x[0]}: {x[1]}\r\n'.encode('utf-8'),
                             self.headers.items())) + b'\r\n' + self.body)


class Request(HttpMessage):
    """
    Http request with parameters.
    """
    def __init__(self,
                 method: str = 'GET',
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


class Response(HttpMessage):
    """
    Http response with parameters.
    """
    def __init__(self,
                 version: str = 'HTTP/1.1',
                 code: int = 200,
                 line: str = '',
                 headers: dict = None,
                 body: bytes = b''):
        self.version = version
        self.code = code
        self.code_description = CODES_DESCRIPTION[code][0]
        super().__init__(line, headers, body)
        self.headers.update({'Content-Length': str(len(body))})

    def is_error(self) -> bool:
        return self.code >= 400

    @property
    def code_description(self):
        return CODES_DESCRIPTION[self.code][0]

    @code_description.setter
    def code_description(self, value):
        self._code_description = value

    @property
    def line(self):
        return f'{self.version} {self.code} {self.code_description}'

    @line.setter
    def line(self, value):
        self._line = value
        if match := RESPONSE_REGEX.match(value):
            self.version, self.code, self.code_description = match.groups()
            self.code = int(self.code)
