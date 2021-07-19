from config import Config
from timed_lru_cache import TimedLruCache
from threading import RLock


class FileHandler:
    config = Config()

    def __init__(self):
        self.cache = TimedLruCache()
        self.lock = RLock()

    def read(self, relative_path):
        with self.lock:
            absolute_path = f'{self.config.root}/{relative_path}'
            if cached_value := self.cache[absolute_path] is not None:
                return cached_value
            else:
                try:
                    with open(absolute_path, mode='rb') as file:
                        return file.read()
                except IOError:
                    if self.config.open_file_cache_errors:
                        self.cache[absolute_path] = b'404 NOT FOUND'
                        return self.cache[absolute_path]
                    else:
                        return b''



