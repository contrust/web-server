from webserver.http_message import HttpMessage


class Request(HttpMessage):
    def __init__(self, raw_data: bytes):
        HttpMessage.__init__(self, raw_data)
        self.method, self.uri, self.version = '', '', ''
        if self.start_line:
            self.method, self.uri, self.version = self.start_line

    def get_start_line(self) -> str:
        return f'{self.method} {self.uri} {self.version}'
