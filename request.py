from config import Config


class Request:
    config = Config()

    def __init__(self, data: bytes):
        headers_index = data.index(b'\r\n') + 2
        body_index = data.index(b'\r\n\r\n') + 4
        self.method, self.uri, self.version = data[:headers_index].decode('utf-8').split()
        self.headers = dict(map(lambda x: x.split(': ', maxsplit=1),
                                data[headers_index: body_index - 4].decode('utf-8').splitlines()))
        self.body = data[body_index:]
        print('created request instance')

    def to_bytes(self) -> bytes:
        print('and then I\'m biting')
        return b' '.join([self.method.encode('utf-8'),
                          self.uri.encode('utf-8'),
                          self.version.encode('utf-8')]) + \
               b'\r\n' + \
               b''.join(map(lambda x: x[0].encode('utf-8') + b': ' +
                            x[1].encode('utf-8') + b'\r\n',
                            self.headers.items())) + \
               b'\r\n' + self.body

    def get_proxy_uri(self) -> str:
        for location in self.config.proxy_pass:
            if location == self.uri[:len(location)]:
                print(self.uri.replace(location, self.config.proxy_pass[location], 1))
                return self.uri.replace(location, self.config.proxy_pass[location], 1)
        return ''

    def get_address(self) -> tuple[str, int]:
        return tuple((pair[0]
                      if len(pair := self.uri.split('/')[2].split(':')) == 2
                      else [pair[0], 80]))
