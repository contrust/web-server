from socket import socket, AF_INET, SOCK_STREAM
from socket_handler import SocketHandler
from request import Request
from config import Config
from file_handler import FileHandler


class Client:
    config = Config()

    def __init__(self, client: socket, file_handler: FileHandler):
        self.client = client
        self.file_handler = file_handler

    def run(self) -> None:
        client_handler = SocketHandler(self.client)
        client_request = Request(client_handler.read())
        if client_request.set_proxy_host_and_relative_path():
            proxy = socket(AF_INET, SOCK_STREAM)
            proxy.connect(client_request.get_address())
            proxy_handler = SocketHandler(proxy)
            proxy_handler.write(client_request.to_bytes())
            client_handler.write(proxy_handler.read())
            while ('Connection' not in client_request.headers or
                   client_request.headers['Connection'] != 'keep-alive'):
                client_request = Request(client_handler.read())
                if not client_request.set_proxy_host_and_relative_path():
                    break
                proxy_handler.write(client_request.to_bytes())
                client_handler.write(proxy_handler.read())
            proxy.close()
        else:
            client_handler.write(self.file_handler.get_response(client_request.uri))
        self.client.close()
        print('I"m so done...')
