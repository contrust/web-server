from web_server.timed_lru_cache import TimedLruCache
from threading import RLock
from web_server.response import Response


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
        self.root = root
        self.index = index
        self.auto_index = auto_index
        self.open_file_cache_errors = open_file_cache_errors

    def get_response(self, relative_path: str) -> Response:
        with self.lock:
            absolute_path = f'{self.root}/{relative_path}' + \
                (('/' if relative_path[-1] != '/' else '') +
                 self.index if self.auto_index else '')
            if (cached_value := self.cache[absolute_path]) is not None:
                return cached_value
            else:
                try:
                    with open(absolute_path, mode='rb') as file:
                        self.cache[absolute_path] = Response(file.read())
                        return self.cache[absolute_path]
                except IOError:
                    if self.open_file_cache_errors:
                        self.cache[absolute_path] = Response(code=404)
                    return Response(code=404)
