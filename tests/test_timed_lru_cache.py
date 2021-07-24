import time
import unittest

from webserver.timed_lru_cache import TimedLruCache


class TestTimedLruCache(unittest.TestCase):
    def test_removing_object_after_reaching_limit(self):
        cache = TimedLruCache(maxsize=2, expiration_time=60)
        cache['dog'] = 1
        cache['cat'] = 2
        self.assertIn('dog', cache)
        cache['tiger'] = 3
        self.assertNotIn('dog', cache)

    def test_removing_least_recently_object(self):
        cache = TimedLruCache(maxsize=2, expiration_time=60)
        cache['mouse'] = 1
        cache['elephant'] = 2
        cache['mouse'] = 1
        self.assertIn('mouse', cache)
        self.assertIn('elephant', cache)
        cache['chicken'] = 3
        self.assertIn('mouse', cache)
        self.assertNotIn('elephant', cache)
        self.assertIn('chicken', cache)

    def test_removing_object_after_expiration_time(self):
        cache = TimedLruCache(maxsize=1, expiration_time=0.05)
        cache['cat'] = 'dog'
        self.assertIsNotNone(cache['cat'])
        time.sleep(0.05)
        self.assertIsNone(cache['cat'])


if __name__ == '__main__':
    unittest.main()
