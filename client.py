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
        if client_request.set_proxy_uri():
            while 1:
                print('hi')
                proxy = socket(AF_INET, SOCK_STREAM)
                proxy.connect(client_request.get_address())
                proxy_handler = SocketHandler(proxy)
                proxy_handler.write(client_request.to_bytes())
                client_handler.write(proxy_handler.read())
                proxy.close()
                client_request = Request(client_handler.read())
                if not client_request.set_proxy_uri():
                    break
        else:
            with open(self.config.root + '/' + client_request.uri + ('/' + self.config.index if self.config.auto_index else ''), mode='rb') as file:
                client_handler.write(b'HTTP/1.1 200 Good\r\nServer: PythonHTTPServer/0.1b\r\nContent-Length: 6\r\n\r\n' + file.read())
        self.client.close()
