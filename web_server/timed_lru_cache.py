from time import time
from threading import RLock


class TimedLruCacheEntry:
    def __init__(self, value, expiration_time: float):
        self.value = value
        self.expiration_time = time() + expiration_time


class TimedLruCache:
    def __init__(self, maxsize, expiration_time):
        self.entries = {}
        self.maxsize = maxsize
        self.expiration_time = expiration_time
        self.lock = RLock()

    def __setitem__(self, key, value):
        with self.lock:
            self.entries = {k: v for k, v in self.entries.items()
                            if v.expiration_time > time()}
            if key not in self.entries:
                if len(self.entries) >= self.maxsize:
                    del self.entries[next(iter(self.entries.keys()))]
                self.entries[key] = TimedLruCacheEntry(value, self.expiration_time)
            else:
                del self.entries[key]
                self.entries[key] = TimedLruCacheEntry(value, self.expiration_time)

    def __getitem__(self, item):
        with self.lock:
            try:
                if item not in self.entries or self.entries[item].expiration_time < time():
                    del self.entries[item]
                self.entries[item].expiration_time = time() + self.expiration_time
                return self.entries[item].value
            except KeyError:
                return None

