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
        proxy = socket(AF_INET, SOCK_STREAM)
        proxy.connect((self.host, self.port))
        client_handler = SocketHandler(self.client)
        proxy_handler = SocketHandler(proxy)
        proxy_handler.write(client_handler.read())
        data = proxy_handler.read()
        print(data)
        client_handler.write(data)
        self.client.close()
        proxy.close()