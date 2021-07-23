from webserver.http_message import HttpMessage


class Request(HttpMessage):
    def __init__(self, byte_request: bytes):
        HttpMessage.__init__(self, byte_request)
        self.method, self.path, self.version = '', '', ''
        if self.start_line:
            self.method, self.path, self.version = self.start_line

    def get_start_line(self) -> str:
        return f'{self.method} {self.path} {self.version}'
