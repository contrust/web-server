from socket import socket, AF_INET, SOCK_STREAM
from socket_handler import SocketHandler
from request import Request
from config import Config


class Client:
    config = Config()

    def __init__(self, client: socket):
        self.client = client

    def run(self) -> None:
        client_handler = SocketHandler(self.client)
        client_request = Request(client_handler.read())
        if proxy_uri := client_request.get_proxy_uri():
            client_request.uri = proxy_uri
            proxy = socket(AF_INET, SOCK_STREAM)
            proxy.connect(client_request.get_address())
            proxy_handler = SocketHandler(proxy)
            proxy_handler.write(client_request.to_bytes())
            client_handler.write(proxy_handler.read())
            proxy.close()
        else:
            pass
        self.client.close()
