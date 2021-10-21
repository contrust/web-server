import multiprocessing
import urllib.request
import pytest
from pathlib import Path
import os

from webserver.config import Config
from webserver.server import Server


@pytest.fixture(autouse=True, scope="session")
def start_servers():
    abspath = os.path.abspath(__file__)
    dirname = os.path.dirname(abspath)
    os.chdir(dirname)
    config = Config()
    config.port = 9080
    config.servers['default']['proxy_pass']['info'] = 'localhost:9090'
    config.servers['default']['proxy_pass']['proxy'] = 'localhost:9090'
    config.servers['default']['proxy_pass']['bad_proxy'] = 'localhost:5432'
    config.servers['default']['python']['bad_function'] = 'wrong.function'
    proxy_config = Config()
    proxy_config.port = 9090
    proxy_config.servers['default']['proxy_pass']['proxy'] = 'localhost:9080'
    config.__post_init__()
    proxy_config.__post_init__()
    server = Server(config)
    proxy_server = Server(proxy_config)
    p1 = multiprocessing.Process(target=server.run)
    p2 = multiprocessing.Process(target=proxy_server.run)
    p1.start()
    p2.start()
    yield
    p1.terminate()
    p2.terminate()


def get_http_response(url: str):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    return response


def test_request_to_index_page():
    response = get_http_response('http://localhost:9080')
    content = response.read()
    assert response.getcode() is 200
    assert b'Index of /' in content


def test_request_to_picture():
    response = get_http_response('http://localhost:9080/test_picture.jpg')
    picture_content = Path('root/test_picture.jpg').read_bytes()
    assert response.getcode() is 200
    assert response.read() == picture_content


def test_request_to_same_function_and_proxy_path():
    response = get_http_response('http://localhost:9080/info/')
    content = response.read()
    assert response.getcode() is 200
    assert content.startswith(b'GET /info/ HTTP/1.1')


def test_request_to_info():
    response = get_http_response('http://localhost:9080/info/blablabla')
    content = response.read()
    assert response.getcode() is 200
    assert content.startswith(b'GET /info/blablabla HTTP/1.1')


def test_request_to_local_page_of_proxy():
    response = get_http_response('http://localhost:9080/proxy/')
    content = response.read()
    assert response.getcode() is 200
    assert b'Index of' in content


def test_request_to_info_of_proxy():
    response = get_http_response('http://localhost:9080/proxy/info/')
    content = response.read()
    assert response.getcode() is 200
    assert content.startswith(b'GET /info/ HTTP/1.1')


def test_request_to_not_existed_local_page():
    with pytest.raises(urllib.error.HTTPError) as e:
        get_http_response('http://localhost:9080/blablaabl')
    assert e.value.code == 404


def test_request_to_not_existed_function():
    with pytest.raises(urllib.error.HTTPError) as e:
        get_http_response('http://localhost:9080/bad_function/')
    assert e.value.code == 500


def test_request_to_not_existed_proxy():
    with pytest.raises(urllib.error.HTTPError) as e:
        get_http_response('http://localhost:9080/bad_proxy/')
    assert e.value.code == 502


def test_request_to_info_of_proxy_of_proxy():
    response = get_http_response('http://localhost:9080/proxy/proxy/info/')
    content = response.read()
    assert response.getcode() is 200
    assert content.startswith(b'GET /info/ HTTP/1.1')
