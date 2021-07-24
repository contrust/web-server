import concurrent.futures
import logging
import os
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from webserver.config import Config
from webserver.index import make_index
from webserver.log import get_log_message
from webserver.proxy import try_get_proxy_request
from webserver.http_message import Request, Response
from webserver.socket_extensions import receive_all
from webserver.timed_lru_cache import TimedLruCache


class Server:
    def __init__(self, config: Config):
        self.config = config
        self.cache = TimedLruCache(config.open_file_cache_size,
                                   config.open_file_cache_inactive_time)
        logging.basicConfig(filename=config.log_file,
                            level=logging.DEBUG,
                            format='%(message)s')

    def run(self) -> None:
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
        while 1:
            start_time = time.time()
            raw_request = receive_all(client,
                                      self.config.keep_alive_timeout)
            if not raw_request:
                break
            request = Request().parse(raw_request)
            response = self.get_response(request)
            client.sendall(bytes(response))
            logging.info(get_log_message(client.getpeername()[0], request,
                                         response, time.time() - start_time))
            if ('Connection' not in request.headers or
                    request.headers['Connection'] != 'keep-alive'):
                break
        client.close()

    def get_response(self, request: Request) \
            -> Response:
        if (proxy_request := try_get_proxy_request(request,
                                                   self.config.proxy_pass)):
            proxy = socket(AF_INET, SOCK_STREAM)
            proxy.connect(proxy_request.host)
            proxy.sendall(bytes(proxy_request))
            raw_proxy_response = receive_all(proxy,
                                             self.config.keep_alive_timeout)
            proxy_response = Response().parse(raw_proxy_response)
            return proxy_response
        else:
            absolute_path = f'{self.config.root}' \
                            f'{request.path.replace("/", os.path.sep)}'
            if self.config.auto_index and absolute_path[-1] == os.path.sep:
                absolute_path += self.config.index
            if cached_value := self.cache[absolute_path]:
                return cached_value
            else:
                try:
                    if os.path.basename(absolute_path) == self.config.index:
                        make_index(absolute_path, self.config.root)
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
