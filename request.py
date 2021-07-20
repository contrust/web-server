import re

from config import Config


class Request:
    config = Config()

    def __init__(self, data: bytes):
        if not data:
            self.uri = ''
            return
        headers_index = data.index(b'\r\n') + 2
        body_index = data.index(b'\r\n\r\n') + 4
        self.method, self.uri, self.version = data[:headers_index].decode('utf-8').split()
        self.headers = dict(map(lambda x: x.split(': ', maxsplit=1),
                                data[headers_index: body_index - 4].decode('utf-8').splitlines()))
        self.body = data[body_index:]
        self.proxy_regex = re.compile(r'(https?://)?(www\.)?(?P<host>[^/]*)(?P<path>/.*)?/?')

    def to_bytes(self) -> bytes:
        return b' '.join([self.method.encode('utf-8'),
                          self.uri.encode('utf-8'),
                          self.version.encode('utf-8')]) + \
               b'\r\n' + \
               b''.join(map(lambda x: x[0].encode('utf-8') + b': ' +
                            x[1].encode('utf-8') + b'\r\n',
                            self.headers.items())) + \
               b'\r\n' + self.body

    def set_proxy_host_and_relative_path(self) -> bool:
        for location in self.config.proxy_pass:
            if location.rstrip('/') == self.uri[:len(location)].rstrip('/'):
                proxy_match = self.proxy_regex.match(self.config.proxy_pass[location])
                self.headers['Host'] = proxy_match.group('host')
                self.uri = '/' + self.uri.replace(location.strip('/'),
                                                  (proxy_match.group('path').strip('/')
                                                   if proxy_match.group('path') is not None else '')).lstrip('/')
                return True
        return False

    def get_address(self) -> tuple:
        return tuple(([pair[0], int(pair[1])]
                      if len(pair := self.headers['Host'].split(':')) == 2
                      else [pair[0], 80]))
