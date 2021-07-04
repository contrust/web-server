from socket import socket, AF_INET, SOCK_STREAM
from socket_handler import SocketHandler
from request import Request
from config import Config


class ProxyPasser:
    def __init__(self, client: socket):
        self.config = Config()
        self.host = self.config.proxy_host
        self.port = self.config.proxy_port
        self.client = client

    def run(self) -> None:
        client_handler = SocketHandler(self.client)
        proxy_request = self.get_proxy_request(client_handler.read())
        proxy = socket(AF_INET, SOCK_STREAM)
        print(f'trying to connect to {self.host}:{self.port}')
        proxy.connect((self.host, self.port))
        print('proxy boss here')
        proxy_handler = SocketHandler(proxy)
        proxy_handler.write(proxy_request)
        print('wrote to your boss')
        data = proxy_handler.read()
        print(data)
        client_handler.write(data)
        self.client.close()
        proxy.close()

    def get_proxy_request(self, data: bytes) -> bytes:
        print('ready to process this data...')
        print(data)
        request = Request(data)
        for location in self.config.proxy_pass:
            if location == request.uri[:len(location)]:
                domain = self.config.proxy_pass[location].split('/')[2]
                print('domain created')
                self.host, self.port = pair[0] if len(pair := domain.split(':', maxsplit=1)) == 2 else pair[0], 80
                self.port = int(self.port)
                print('host and port are done')
                request.uri = request.uri.replace(location, self.config.proxy_pass[location], 1)
                print('uri is done')
                return request.to_bytes()
        return b''
