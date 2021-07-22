import os
from threading import RLock
from webserver.timed_lru_cache import TimedLruCache
from webserver.response import Response
from webserver.index_maker import make_index


class FileHandler:
    def __init__(self,
                 root: str,
                 index: str,
                 auto_index: bool,
                 open_file_cache_size: int,
                 open_file_cache_errors: bool,
                 open_file_cache_inactive_time: float,
                 **kwargs):
        self.cache = TimedLruCache(maxsize=open_file_cache_size,
                                   expiration_time=open_file_cache_inactive_time)
        self.lock = RLock()
        self.root = f'{os.path.dirname(__file__)}{os.path.sep}{root}' if not os.path.isabs(root) else root
        self.index = index
        self.auto_index = auto_index
        self.open_file_cache_errors = open_file_cache_errors

    def get_response(self, relative_path: str) -> Response:
        with self.lock:
            absolute_path = f'{self.root}{relative_path.replace("/", os.path.sep)}'
            if self.auto_index and absolute_path[-1] == os.path.sep:
                absolute_path += self.index
            if (cached_value := self.cache[absolute_path]) is not None:
                return cached_value
            else:
                try:
                    if absolute_path.endswith(os.path.sep + self.index):
                        make_index(absolute_path, self.root)
                    with open(absolute_path, mode='rb') as file:
                        response = Response(file.read())
                        if not absolute_path.endswith(os.path.sep + self.index):
                            self.cache[absolute_path] = response
                        return response
                except IOError:
                    if self.open_file_cache_errors:
                        self.cache[absolute_path] = Response(code=404)
                    return Response(code=404)
