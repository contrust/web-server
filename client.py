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
        if client_request.set_proxy_uri():
            while 1:
                proxy = socket(AF_INET, SOCK_STREAM)
                proxy.connect(client_request.get_address())
                proxy_handler = SocketHandler(proxy)
                proxy_handler.write(client_request.to_bytes())
                client_handler.write(proxy_handler.read())
                proxy.close()
                client_request = Request(client_handler.read())
                if (not client_request.set_proxy_uri() or
                    'Connection' not in client_request.headers or
                        client_request.headers['Connection'] != 'keep-alive'):
                    break
        else:
            client_handler.write(b'HTTP/1.1 200 Good\r\nServer: PythonHTTPServer/0.1b\r\nContent-Length: 13\r\n\r\n' +
                                 self.file_handler.read(client_request.uri))
        self.client.close()
