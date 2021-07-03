class Request:
    def __init__(self, data: bytes):
        headers_index = data.index(b'\r\n') + 2
        body_index = data.index(b'\r\n\r\n') + 4
        self.method, self.uri, self.version = data[:headers_index].split()
        self.headers = dict(map(lambda x: x.split(b': ', maxsplit=1),
                                data[headers_index: body_index - 4].splitlines()))
        self.body = data[body_index:]
        print('created request instance')

    def to_bytes(self) -> bytes:
        print('and then I\'m biting')
        return b' '.join([self.method, self.uri, self.version]) + b'\r\n' + \
            b''.join(map(lambda x: x[0] + b': ' + x[1] + b'\r\n', self.headers.items())) + \
            b'\r\n' + self.body
