from socket import socket, AF_INET, SOCK_STREAM
from socket_handler import SocketHandler
from request import Request


class ProxyPasser:
    def __init__(self, client: socket, host: str, port: int):
        self.host = host
        self.port = port
        self.client = client
        self.proxy = socket(AF_INET, SOCK_STREAM)
        self.proxy.connect((self.host, self.port))
        print('socket connected')

    def run(self) -> None:
        print('hi')
        client_handler = SocketHandler(self.client)
        print('handle client')
        proxy_handler = SocketHandler(self.proxy)
        print('handle proxy')
        request = Request(client_handler.read())
        print('client read')
        request.uri = f'http://{self.host}{request.uri.decode(encoding="utf-8")}' \
            .encode(encoding='utf-8')
        print(request.to_bytes())
        proxy_handler.write(request.to_bytes())
        print('proxy wrote')
        client_handler.write(proxy_handler.read())
        print('client wrote')