import unittest

from webserver.http_message import Request
from webserver.proxy import try_get_proxy_request


class TestProxy(unittest.TestCase):
    def test_none_if_proxy_pass_is_empty(self):
        request = Request()
        proxy_pass = {}
        proxy_request = try_get_proxy_request(request, proxy_pass)
        self.assertIsNone(proxy_request)

    def test_none_if_proxy_pass_not_matches(self):
        request = Request()
        proxy_pass = {'dog': 'localhost:8080'}
        proxy_request = try_get_proxy_request(request, proxy_pass)
        self.assertIsNone(proxy_request)

    def test_not_none_if_proxy_pass_matches(self):
        request = Request(path='/dog/')
        proxy_pass = {'dog': 'localhost:8080'}
        proxy_request = try_get_proxy_request(request, proxy_pass)
        self.assertIsNotNone(proxy_request)

    def test_change_path_after_matching(self):
        request = Request(path='/dog/lol')
        proxy_pass = {'dog': 'localhost:8080'}
        proxy_request = try_get_proxy_request(request, proxy_pass)
        self.assertEqual(proxy_request.path, '/lol')

    def test_change_host_after_matching(self):
        request = Request(path='/dog/lol')
        proxy_pass = {'dog': 'localhost:7080'}
        proxy_request = try_get_proxy_request(request, proxy_pass)
        self.assertEqual(proxy_request.headers['Host'], 'localhost:7080')

    def test_host_without_http_and_www_part(self):
        request = Request(path='/dog/lol')
        proxy_pass = {'dog': 'https://www.google.com'}
        proxy_request = try_get_proxy_request(request, proxy_pass)
        self.assertEqual(proxy_request.headers['Host'], 'google.com')


if __name__ == '__main__':
    unittest.main()