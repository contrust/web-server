import unittest

from webserver.function import try_get_function_response
from webserver.http_message import Request, Response


def get_request_path(request: Request) -> Response:
    return Response(body=request.path.encode('utf-8'))


class TestFunction(unittest.TestCase):
    def test_none_when_no_matching_paths(self):
        request = Request(path='/hello/')
        functions = {'aloha': 'webserver.function.get_request_information'}
        response = try_get_function_response(request, functions)
        self.assertIsNone(response)

    def test_error_when_module_not_found(self):
        request = Request(path='/hello/')
        functions = {'hello': 'websver.fuction.get_request_information'}
        response = try_get_function_response(request, functions)
        self.assertTrue(response.is_error())

    def test_not_error_response_from_webserver_function(self):
        request = Request(path='/hello/')
        functions = {'hello': 'webserver.function.get_request_information'}
        response = try_get_function_response(request, functions)
        self.assertFalse(response.is_error())

    def test_not_webserver_function_returns_valid_response(self):
        request = Request(path='/hello/')
        functions = {'hello': 'tests.test_function.get_request_path'}
        response = try_get_function_response(request, functions)
        self.assertEqual(response.body, b'/hello/')





if __name__ == '__main__':
    unittest.main()
