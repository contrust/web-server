import re
from socket import socket, AF_INET, SOCK_STREAM
from webserver.socket_handler import SocketHandler
from webserver.request import Request
from webserver.config import Config
from webserver.file_handler import FileHandler


class Client:
    def __init__(self, client: socket, config: Config, file_handler: FileHandler):
        self.client = client
        self.config = config
        self.file_handler = file_handler
        self.proxy_regex = re.compile(r'(https?://)?(www\.)?(?P<host>[^/]*)(?P<path>/.*)?')

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
            if request.uri.startswith(location + '/'):
                proxy_match = self.proxy_regex.match(self.config.proxy_pass[location])
                host, path = proxy_match.group('host'), proxy_match.group('path')
                request.headers['Host'] = host
                request.uri = request.uri.replace(location, path if path else '')
                return True
        return False
