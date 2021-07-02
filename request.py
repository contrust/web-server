class Request:
    def __init__(self, data: bytes):
        headers_index = data.index(b'\r\n') + 2
        body_index = data.index(b'\r\n\r\n') + 4
        data = data.decode('utf-8')
        self.method, self.uri, self.version = data[:headers_index].split()
        self.headers = dict(map(lambda x: x.split(': ', maxsplit=1),
                                data[headers_index: body_index - 4].splitlines()))
        self.body = data[body_index:]
