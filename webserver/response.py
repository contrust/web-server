from webserver.http_message import HttpMessage

CODES_DESCRIPTION = {
    200: 'Success',
    304: 'Not Modified',
    404: 'Not Found',
}


class Response(HttpMessage):
    def __init__(self, raw_response: bytes = b'', body: bytes = b'', code: int = 200):
        HttpMessage.__init__(self, raw_response)
        self.version, self.code, self.code_meaning = '', '', ''
        if self.start_line:
            self.version, self.code, self.code_meaning = self.start_line
        else:
            self.version = 'HTTP/1.1'
            self.code = str(code)
            self.code_meaning = CODES_DESCRIPTION[code]
            self.start_line = self.get_start_line()
            self.headers = {
                'Content-Length': str(len(body))
            }
            self.body = body

    def get_start_line(self) -> str:
        return f'{self.version} {self.code} {self.code_meaning}'
