import os
import queue
import sys
import threading
import time
import urllib

import pytest
import requests

from webserver.config import Config
from webserver.server import Server


def run_server(config: Config) -> None:
    config.__post_init__()
    server = Server(config)
    server.run()


def get_http_response(url: str):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    return response


def test_index_request():
    config = Config()
    config.port = 9080
    t1 = threading.Thread(target=run_server, args=(config,))
    t1.setDaemon(True)
    t1.start()
    time.sleep(1)
    response = get_http_response('http://localhost:9080')
    content = response.read()
    assert response.getcode() is 200
    assert b'Index of' in content


def test_picture_request():
    config = Config()
    config.port = 9050
    t1 = threading.Thread(target=run_server, args=(config,))
    t1.setDaemon(True)
    t1.start()
    time.sleep(1)
    response = get_http_response('http://localhost:9080/test_picture.jpg')
    assert response.getcode() is 200


def test_right_priority_response():
    config = Config()
    config.port = 9040
    config.servers['default']['proxy_pass']['info'] = 'localhost:9040'
    t1 = threading.Thread(target=run_server, args=(config,))
    t1.setDaemon(True)
    t1.start()
    time.sleep(1)
    response = get_http_response('http://localhost:9040/info/')
    content = response.read()
    assert response.getcode() is 200
    assert b'GET /info/ HTTP/1.1' in content


def test_info_request():
    config = Config()
    config.port = 9090
    t1 = threading.Thread(target=run_server, args=(config,))
    t1.setDaemon(True)
    t1.start()
    time.sleep(1)
    response = get_http_response('http://localhost:9090/info/')
    content = response.read()
    assert response.getcode() is 200
    assert b'GET /info/ HTTP/1.1' in content
    response = get_http_response('http://localhost:9090/info/blablabla')
    content = response.read()
    assert response.getcode() is 200
    assert b'GET /info/blablabla HTTP/1.1' in content


def test_proxy_request():
    config1 = Config()
    config2 = Config()
    config1.port = 9092
    config1.servers['default']['proxy_pass']['proxy'] = 'localhost:9093'
    config2.port = 9093
    config2.servers['default']['log_file'] = 'log2.txt'
    t1 = threading.Thread(target=run_server, args=(config1,))
    t2 = threading.Thread(target=run_server, args=(config2,))
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    time.sleep(1)
    response = get_http_response('http://localhost:9092/proxy/')
    content = response.read()
    assert response.getcode() is 200
    assert b'Index of' in content
    response = get_http_response('http://localhost:9092/proxy/info/')
    content = response.read()
    assert response.getcode() is 200
    assert b'GET /info/ HTTP/1.1' in content


def test_not_found_request():
    config = Config()
    config.port = 9070
    t1 = threading.Thread(target=run_server, args=(config,))
    t1.setDaemon(True)
    t1.start()
    time.sleep(1)
    with pytest.raises(urllib.error.HTTPError) as e:
        get_http_response('http://localhost:9070/blablaabl')
    assert e.value.code == 404


def test_bad_gateway_request():
    config = Config()
    config.port = 9060
    config.servers['default']['proxy_pass']['bad'] = 'blablallaafasdfb'
    t1 = threading.Thread(target=run_server, args=(config,))
    t1.setDaemon(True)
    t1.start()
    time.sleep(1)
    with pytest.raises(urllib.error.HTTPError) as e:
        get_http_response('http://localhost:9060/bad/')
    assert e.value.code == 502

