from threading import RLock
from time import time


class TimedLruCacheEntry:
    def __init__(self, value, expiration_time: float):
        self.value = value
        self.expiration_time = time() + expiration_time


class TimedLruCache:
    """
    Lru cache which removes it's items when
    they haven't been used for a certain time.
    """
    def __init__(self, maxsize, expiration_time):
        self.entries = {}
        self.maxsize = maxsize
        self.expiration_time = expiration_time
        self.lock = RLock()

    def __setitem__(self, key, value):
        with self.lock:
            if key not in self:
                if len(self.entries) >= self.maxsize:
                    del self.entries[next(iter(self.entries.keys()))]
                self.entries[key] = TimedLruCacheEntry(value,
                                                       self.expiration_time)
            else:
                del self.entries[key]
                self.entries[key] = TimedLruCacheEntry(value,
                                                       self.expiration_time)

    def __getitem__(self, item):
        with self.lock:
            if item in self:
                self.entries[item]\
                    .expiration_time = time() + self.expiration_time
                return self.entries[item].value
            else:
                return None

    def __contains__(self, item):
        with self.lock:
            self.update()
            return item in self.entries

    def update(self):
        with self.lock:
            self.entries = {k: v for k, v in self.entries.items()
                            if v.expiration_time > time()}
