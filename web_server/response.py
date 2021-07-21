from web_server.response_codes_meaning import codes_meaning


class Response:
    def __init__(self, body: bytes = b'', code: int = 200):
        self.version = 'HTTP/1.1'
        self.code = str(code)
        self.code_meaning = codes_meaning[code]
        self.headers = {
            'Content-Length': str(len(body))
        }
        self.body = body

    def to_bytes(self) -> bytes:
        return b' '.join([self.version.encode('utf-8'),
                          self.code.encode('utf-8'),
                          self.code_meaning.encode('utf-8')]) + \
               b'\r\n' + \
               b''.join(map(lambda x: x[0].encode('utf-8') + b': ' +
                            x[1].encode('utf-8') + b'\r\n',
                            self.headers.items())) + \
               b'\r\n' + self.body
