import re

HTTP_REGEX = re.compile(rb'([^\s]+)\s([^\s]+)\s(.*?)\r\n(?P<headers>(?:.*?: .*?\r\n)+)\r\n(?P<body>.*)', re.DOTALL)


class HttpMessage:
    def __init__(self, raw_message: bytes = b''):
        match = HTTP_REGEX.match(raw_message)
        self.start_line, self.headers, self.body = [], {}, b''
        if match:
            self.start_line = map(lambda x: x.decode('utf-8'), [match.group(1), match.group(2), match.group(3)])
            if match.group('headers'):
                self.headers = dict(map(lambda x: x.split(': ', maxsplit=1),
                                        match.group('headers').decode('utf-8').splitlines()))
            if match.group('body'):
                self.body = match.group('body')

    def get_start_line(self) -> str:
        return ' '.join(self.start_line)

    def get_hostname_and_port(self) -> tuple:
        return tuple(([pair[0], int(pair[1])]
                      if len(pair := self.headers['Host'].split(':')) == 2
                      else [pair[0], 80]))

    def __bytes__(self) -> bytes:
        return (self.get_start_line().encode('utf-8') +
                b'\r\n' +
                b''.join(map(lambda x: f'{x[0]}: {x[1]}\r\n'.encode('utf-8'),
                             self.headers.items())) +
                b'\r\n' + self.body) if self.start_line else ''
