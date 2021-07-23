import os
from threading import RLock
from webserver.config import Config
from webserver.request import Request
from webserver.timed_lru_cache import TimedLruCache
from webserver.response import Response
from webserver.index_maker import make_index


class FileHandler:
    def __init__(self, config: Config):
        self.config = config
        self.cache = TimedLruCache(config.open_file_cache_size, config.open_file_cache_inactive_time)
        self.lock = RLock()
        self.root = f'{os.path.dirname(__file__)}{os.path.sep}{config.root}' if not os.path.isabs(config.root)\
            else config.root

    def get_response(self, request: Request) -> Response:
        with self.lock:
            request.headers['Host'] = f'{self.config.hostname}:{self.config.port}'
            absolute_path = f'{self.root}{request.uri.replace("/", os.path.sep)}'
            if self.config.auto_index and absolute_path[-1] == os.path.sep:
                absolute_path += self.config.index
            if (cached_value := self.cache[absolute_path]) is not None:
                return cached_value
            else:
                try:
                    if absolute_path.endswith(os.path.sep + self.config.index):
                        make_index(absolute_path, self.root)
                    with open(absolute_path, mode='rb') as file:
                        response = Response(body=file.read())
                        if not absolute_path.endswith(os.path.sep + self.config.index):
                            self.cache[absolute_path] = response
                        return response
                except IOError:
                    if self.config.open_file_cache_errors:
                        self.cache[absolute_path] = Response(code=404)
                    return Response(code=404)
