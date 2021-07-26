import concurrent.futures
import logging
import os
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from timeit import default_timer as timer

from webserver.config import Config
from webserver.function import try_get_function_response
from webserver.http_message import Request, Response
from webserver.index import make_index
from webserver.log import get_log_message
from webserver.proxy import try_get_proxy_response
from webserver.socket_extensions import receive_all
from webserver.timed_lru_cache import TimedLruCache


class Server:
    def __init__(self, config: Config):
        self.config = config
        self.cache = TimedLruCache(config.open_file_cache_size,
                                   config.open_file_cache_inactive_time)

    def run(self) -> None:
        """
        Run loop of accepting new connection to the server.
        """
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.config.max_threads) as executor:
            with socket(AF_INET, SOCK_STREAM) as server:
                server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                server.bind((self.config.hostname, self.config.port))
                server.listen()
                print(f'Server launched with '
                      f'{self.config.hostname}:{self.config.port}')
                while 1:
                    client, address = server.accept()
                    executor.submit(self.handle_client, client=client)

    def handle_client(self, client: socket) -> None:
        """
        Run loop of giving responses to client's requests.
        """
        while 1:
            start_time = timer()
            raw_request = receive_all(client,
                                      self.config.keep_alive_timeout)
            if not raw_request:
                break
            request = Request().parse(raw_request)
            response = self.get_response(request)
            client.sendall(bytes(response))
            end_time = timer()
            if (hostname := request.headers.get('Host',
                                                ' ')) in self.config.servers:
                logging.basicConfig(
                    filename=self.config.servers[hostname]['log_file'],
                    level=logging.DEBUG,
                    format='%(message)s',
                    force=True)
                logging.info(get_log_message(client.getpeername()[0], request,
                                             response, end_time - start_time))
            if ('Connection' not in request.headers or
                    request.headers['Connection'] != 'keep-alive'):
                break
        client.close()

    def get_response(self, request: Request) \
            -> Response:
        """
        Get server's response to request.
        """
        hostname = request.headers.get('Host', ' ')
        if hostname in self.config.servers:
            if (function_response := try_get_function_response(
                    request,
                    self.config.servers[hostname]['python'])):
                response = function_response
            elif (proxy_response := try_get_proxy_response(
                    request,
                    self.config.servers[hostname]['proxy_pass'],
                    self.config.keep_alive_timeout)):
                response = proxy_response
            else:
                response = self.get_local_response(request)
        else:
            response = Response(code=404)
        return response

    def get_local_response(self, request: Request) -> Response:
        hostname = request.headers.get('Host', ' ')
        absolute_path = f'{self.config.servers[hostname]["root"]}' \
                        f'{request.path.replace("/", os.path.sep)}'
        is_auto_index = (self.config.servers[hostname]['auto_index'] and
                         absolute_path[-1] == os.path.sep)
        try:
            if is_auto_index:
                make_index(absolute_path + self.config.index,
                           self.config.servers[hostname]['root'])
            if response := self.cache[absolute_path]:
                return response
            with open(absolute_path +
                      (self.config.index if is_auto_index else ''),
                      mode='rb') as file:
                response = Response(body=file.read())
        except IOError:
            response = Response(code=404)
        if ((not response.is_error() or
             self.config.open_file_cache_errors) and not is_auto_index):
            self.cache[absolute_path] = response
        return response
