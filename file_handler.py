import time

from config import Config
from timed_lru_cache import TimedLruCache
from threading import RLock
from response import Response


class FileHandler:
    config = Config()

    def __init__(self):
        self.cache = TimedLruCache()
        self.lock = RLock()

    def get_response(self, relative_path: str) -> bytes:
        with self.lock:
            absolute_path = f'{self.config.root}/{relative_path}' + \
                (('/' if relative_path[-1] != '/' else '') +
                 self.config.index if self.config.auto_index else '')
            if (cached_value := self.cache[absolute_path]) is not None:
                return cached_value.to_bytes()
            else:
                try:
                    with open(absolute_path, mode='rb') as file:
                        response = Response(file.read())
                        if int(response.code) < 400 or self.config.open_file_cache_errors:
                            self.cache[absolute_path] = response
                        return response.to_bytes()
                except IOError:
                    if self.config.open_file_cache_errors:
                        self.cache[absolute_path] = Response(code=404)
                    return Response(code=404).to_bytes()



