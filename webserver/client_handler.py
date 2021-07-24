import logging
import os
import re
import copy
from time import time
from datetime import datetime, timezone
from socket import socket, AF_INET, SOCK_STREAM
from select import select

from webserver.config import Config
from webserver.index_maker import make_index
from webserver.request import Request
from webserver.response import Response
from webserver.timed_lru_cache import TimedLruCache

PROXY_REGEX = re.compile(r'(https?://)?(www\.)?(?P<host>[^/]*)(?P<path>/.*)?')


def receive_all(sock, timeout) -> bytes:
    total_data = []
    sock.setblocking(0)
    ready = select([sock], [], [], timeout)
    while ready[0]:
        try:
            data = sock.recv(8192)
            total_data.append(data)
            if not data:
                break
        except BlockingIOError:
            return b''.join(total_data)
    return b'timeout'


def get_log_string(client: socket,
                   request: Request,
                   response: Response,
                   processing_time: float) -> str:
    return f"{client.getpeername()[0]} - - " \
           f"[{datetime.now(timezone.utc).strftime('%d/%b/%Y:%H:%M:%S %z')}]" \
           f" \"" \
           f"{request.line}\" " \
           f"{response.code} {response.headers.get('Content-Length', 0)} \"" \
           f"{request.headers.get('Referer', '-')}\" \"" \
           f"{request.headers.get('User-Agent', '-')}\" " \
           f"{int(processing_time * 1000)}"


class ClientHandler:
    def __init__(self, client: socket, config: Config, cache: TimedLruCache):
        self.config = config
        self.cache = cache
        self.client = client
        self.proxy = None

    def run(self) -> None:
        while 1:
            start_time = time()
            raw_request = receive_all(self.client,
                                      self.config.keep_alive_timeout)
            if raw_request == b'timeout':
                break
            request = Request().parse(raw_request)
            response = self.get_response(request)
            raw_response = bytes(response)
            self.client.sendall(raw_response)
            print('nu da...')
            logging.info(get_log_string(self.client, request,
                                        response, time() - start_time))
            if ('Connection' not in request.headers or
                    request.headers['Connection'] != 'keep-alive'):
                break
        if self.proxy:
            self.proxy.close()
        self.client.close()

    def get_response(self, request: Request) -> Response:
        if (proxy_request := self.try_get_proxy_request(request)) is not None:
            if not self.proxy:
                self.proxy = socket(AF_INET, SOCK_STREAM)
                self.proxy.connect(proxy_request.host)
            self.proxy.sendall(bytes(proxy_request))
            raw_proxy_response = receive_all(self.proxy,
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
                        if not os.path.basename(absolute_path) == \
                                self.config.index:
                            self.cache[absolute_path] = response
                except IOError:
                    response = Response(code=404)
                    if self.config.open_file_cache_errors:
                        self.cache[absolute_path] = response
                return response

    def try_get_proxy_request(self, request: Request) -> Request or None:
        for location in self.config.proxy_pass:
            if request.path.startswith(f'/{location}/') or not location:
                proxy_request = copy.deepcopy(request)
                proxy_match = PROXY_REGEX.match(
                    self.config.proxy_pass[location])
                host, path = proxy_match.group('host'), proxy_match.group(
                    'path')
                proxy_request.headers['Host'] = host
                proxy_request.path =\
                    proxy_request.path.replace(f'/{location}',
                                               (path if path else '') +
                                               ('/' if not location else ''),
                                               1)
                return proxy_request
        return None
