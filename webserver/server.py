import concurrent.futures
import logging
import os
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from timeit import default_timer as timer

from webserver.config import Config
from webserver.http_message import Request, Response
from webserver.index import make_index
from webserver.log import get_log_message
from webserver.proxy import try_get_proxy_request
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
        hostname = request.host[0]
        logging.basicConfig(filename=self.config.servers[hostname]['log_file'],
                            level=logging.DEBUG,
                            format='%(message)s')
        if (proxy_request := try_get_proxy_request(request,
                                                   self.config.servers[
                                                       hostname][
                                                       'proxy_pass'])):
            proxy = socket(AF_INET, SOCK_STREAM)
            proxy.connect(proxy_request.host)
            proxy.sendall(bytes(proxy_request))
            raw_proxy_response = receive_all(proxy,
                                             self.config.keep_alive_timeout)
            proxy_response = Response().parse(raw_proxy_response)
            proxy.close()
            return proxy_response
        else:
            absolute_path = f'{self.config.servers[hostname]["root"]}' \
                            f'{request.path.replace("/", os.path.sep)}'
            if (self.config.servers[hostname]['auto_index'] and
                    absolute_path[-1] == os.path.sep):
                absolute_path += self.config.index
            if cached_value := self.cache[absolute_path]:
                return cached_value
            else:
                try:
                    if os.path.basename(absolute_path) == self.config.index:
                        make_index(absolute_path,
                                   self.config.servers[hostname]['root'])
                    with open(absolute_path, mode='rb') as file:
                        response = Response(body=file.read())
                        if not (os.path.basename(absolute_path) ==
                                self.config.index):
                            self.cache[absolute_path] = response
                except IOError:
                    response = Response(code=404)
                    if self.config.open_file_cache_errors:
                        self.cache[absolute_path] = response
                return response
