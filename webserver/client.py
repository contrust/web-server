import logging
import re
import socket
from socket import socket, AF_INET, SOCK_STREAM
from webserver.socket_handler import SocketHandler
from webserver.request import Request
from webserver.response import Response
from webserver.file_handler import FileHandler


class Client:
    def __init__(self, client: socket, file_handler: FileHandler):
        self.config = file_handler.config
        self.client_handler = SocketHandler(sock=client, timeout=self.config.keep_alive_timeout)
        self.proxy_handler = None
        self.file_handler = file_handler
        self.proxy_regex = re.compile(r'(https?://)?(www\.)?(?P<host>[^/]*)(?P<path>/.*)?')

    def run(self) -> None:
        while 1:
            data = self.client_handler.read()
            if data == b'timeout':
                break
            request = Request(byte_request=data)
            initial_request_path = request.path
            logging.info(f'processing request {request.method} {request.path}')
            response = self.get_response(request)
            self.client_handler.write(bytes(response))
            logging.info(f'received request {request.method} {initial_request_path}, '
                         f'returned response {response.code} ({response.code_meaning})')
            if ('Connection' not in request.headers or
                    request.headers['Connection'] != 'keep-alive'):
                break
        if self.proxy_handler:
            self.proxy_handler.socket.close()
        self.client_handler.socket.close()

    def get_response(self, request: Request) -> Response:
        if self.set_proxy_host_and_relative_path(request):
            if not self.proxy_handler:
                proxy = socket(AF_INET, SOCK_STREAM)
                proxy.connect(request.get_hostname_and_port())
                self.proxy_handler = SocketHandler(sock=proxy, timeout=self.config.keep_alive_timeout)
            self.proxy_handler.write(bytes(request))
            return Response(raw_response=self.proxy_handler.read())
        else:
            return self.file_handler.get_response(request)

    def set_proxy_host_and_relative_path(self, request: Request) -> bool:
        for location in self.config.proxy_pass:
            if request.path.startswith(f'/{location}/') or not location:
                proxy_match = self.proxy_regex.match(self.config.proxy_pass[location])
                host, path = proxy_match.group('host'), proxy_match.group('path')
                request.headers['Host'] = host
                if location:
                    request.path = request.path.replace(f'/{location}', path if path else '')
                elif path:
                    request.path = request.path.replace('/', f'{path}/', 1)
                return True
        return False
