import unittest
import re

from webserver.http_message import Request, Response
from webserver.log import get_log_message

LOG_MESSAGE_REGEX = re.compile(r'(?P<client>(?:\d{1,3}\.){3}\d{1,3})\s+-\s+-\s+'
                               r'\[(?P<date>\d{2}.\w{3}.\d{4}).*\]\s+"'
                               r'(?P<method>GET|PUT|POST|HEAD|OPTIONS|DELETE)'
                               r'\s+(?P<path>.*?)\s+[A-Z]{3,5}/\d\.\d?"'
                               r'\s+\d+\s+\d+\s+".*"\s+'
                               r'"(?P<user_agent>.*)"'
                               r'(?:\s+(?P<processing_time>\d+))?')


class TestLog(unittest.TestCase):
    def test_matches_format(self):
        request = Request()
        response = Response()
        log_message = get_log_message('127.0.0.1', request, response, 10)
        self.assertIsNotNone(LOG_MESSAGE_REGEX.match(log_message))


if __name__ == '__main__':
    unittest.main()
