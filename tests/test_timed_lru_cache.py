import time
import unittest
from web_server.timed_lru_cache import TimedLruCache


class TimedLruCacheSize(unittest.TestCase):
    def test_removing_object_after_reaching_limit(self):
        cache = TimedLruCache(maxsize=3, expiration_time=60)
        cache['dog'] = 1
        cache['cat'] = 2
        cache['snake'] = 3
        self.assertIn('dog', cache)
        cache['tiger'] = 4
        self.assertNotIn('dog', cache)


class TimedLruCacheTime(unittest.TestCase):
    def test_removing_object_after_expiration_time(self):
        cache = TimedLruCache(maxsize=1, expiration_time=0.05)
        cache['cat'] = 'dog'
        self.assertIsNotNone(cache['cat'])
        time.sleep(0.05)
        self.assertIsNone(cache['cat'])


if __name__ == '__main__':
    unittest.main()
