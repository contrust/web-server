from socket import socket, AF_INET, SOCK_STREAM
from socket_handler import SocketHandler
from request import Request
from config import Config
from file_handler import FileHandler


class Client:
    def __init__(self, client: socket, config: Config, file_handler: FileHandler):
        self.client = client
        self.config = config
        self.file_handler = file_handler

    def run(self) -> None:
        client_handler = SocketHandler(self.client, timeout=self.config.connection_timeout)
        client_request = Request(client_handler.read())
        if self.set_proxy_host_and_relative_path(client_request):
            proxy = socket(AF_INET, SOCK_STREAM)
            proxy.connect(client_request.get_address())
            proxy_handler = SocketHandler(proxy, timeout=self.config.connection_timeout)
            proxy_handler.write(client_request.to_bytes())
            client_handler.write(proxy_handler.read())
            while ('Connection' not in client_request.headers or
                   client_request.headers['Connection'] != 'keep-alive'):
                client_request = Request(client_handler.read())
                if not self.set_proxy_host_and_relative_path(client_request):
                    break
                proxy_handler.write(client_request.to_bytes())
                client_handler.write(proxy_handler.read())
            proxy.close()
        else:
            client_handler.write(self.file_handler.get_response(client_request.uri).to_bytes())
        self.client.close()

    def set_proxy_host_and_relative_path(self, request: Request) -> bool:
        for location in self.config.proxy_pass:
            if location.rstrip('/') == request.uri[:len(location)].rstrip('/'):
                proxy_match = request.proxy_regex.match(self.config.proxy_pass[location])
                request.headers['Host'] = proxy_match.group('host')
                request.uri = '/' + request.uri.replace(location.strip('/'),
                                                        (proxy_match.group('path').strip('/')
                                                        if proxy_match.group('path') is not None else '')).lstrip('/')
                return True
        return False
