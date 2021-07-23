import re
import socket
from socket import socket, AF_INET, SOCK_STREAM
from webserver.socket_handler import SocketHandler
from webserver.request import Request
from webserver.response import Response
from webserver.config import Config
from webserver.file_handler import FileHandler


class Client:
    def __init__(self, client: socket, config: Config, file_handler: FileHandler):
        self.client = client
        self.config = config
        self.file_handler = file_handler
        self.proxy_regex = re.compile(r'(https?://)?(www\.)?(?P<host>[^/]*)(?P<path>/.*)?')

    def run(self) -> None:
        client_handler = SocketHandler(sock=self.client, timeout=self.config.connection_timeout)
        proxy_handler = None
        while 1:
            data = client_handler.read()
            if data == b'timeout':
                break
            client_request = Request(raw_data=data)
            if self.set_proxy_host_and_relative_path(client_request):
                if not proxy_handler:
                    proxy = socket(AF_INET, SOCK_STREAM)
                    proxy.connect(client_request.get_hostname_and_port())
                    proxy_handler = SocketHandler(sock=proxy, timeout=self.config.connection_timeout)
                proxy_handler.write(bytes(client_request))
                response = Response(raw_data=proxy_handler.read())
                client_handler.write(bytes(response))
            else:
                response = self.file_handler.get_response(client_request.uri)
                client_handler.write(bytes(response))
            if ('Connection' not in client_request.headers or
                    client_request.headers['Connection'] != 'keep-alive'):
                break
        if proxy_handler:
            proxy_handler.socket.close()
        self.client.close()

    def set_proxy_host_and_relative_path(self, request: Request) -> bool:
        if request.uri:
            for location in self.config.proxy_pass:
                if request.uri.startswith(location + '/'):
                    proxy_match = self.proxy_regex.match(self.config.proxy_pass[location])
                    host, path = proxy_match.group('host'), proxy_match.group('path')
                    request.headers['Host'] = host
                    request.uri = request.uri.replace(location, path if path else '')
                    return True
        return False
