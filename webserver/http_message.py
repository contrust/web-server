import re

HTTP_MESSAGE_REGEX = re.compile(
    rb'(?P<line>([^\s]+)\s([^\s]+)\s(.*?))\r\n(?P<headers>(?:.*?: .*?\r\n)*)\r\n(?P<body>.*)', re.DOTALL)
HOST_REGEX = re.compile(r'(?P<hostname>[^:]+)(:(?P<port>\d{1,5}))?')


class HttpMessage:
    def __init__(self, line: str = '', headers: dict = None, body: bytes = b''):
        self.line = line
        self.headers = headers if headers else {}
        self.body = body

    def parse(self, message: bytes):
        match = HTTP_MESSAGE_REGEX.match(message)
        if match:
            self.line = match.group('line').decode('utf-8')
            if match.group('headers'):
                self.headers = dict(map(lambda x: x.split(': ', maxsplit=1),
                                        match.group('headers').decode('utf-8').splitlines()))
            if match.group('body'):
                self.body = match.group('body')
            return self
        raise ValueError

    @property
    def host(self) -> tuple:
        match = HOST_REGEX.match(self.headers.get('Host', ''))
        hostname, port = match.group('hostname'), int(port) if (port := match.group('port')) else 80
        return tuple([hostname, port])

    def __bytes__(self) -> bytes:
        return (self.line.encode('utf-8') + b'\r\n' +
                b''.join(map(lambda x: f'{x[0]}: {x[1]}\r\n'.encode('utf-8'),
                             self.headers.items())) + b'\r\n' + self.body)
