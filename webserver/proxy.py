import copy
import re
import socket

from webserver.http_message import Request, Response
from webserver.socket_extensions import receive_all

PROXY_REGEX = re.compile(r'(https?://)?(www\.)?(?P<host>[^/]*)(?P<path>/.*)?')


def try_get_proxy_request(request: Request, proxy_pass: dict) \
        -> Request or None:
    """
    Try to proxy request and return it, otherwise return None.
    """
    for location in proxy_pass:
        if request.path.startswith(f'/{location}/') or not location:
            proxy_request = copy.deepcopy(request)
            proxy_match = PROXY_REGEX.match(proxy_pass[location])
            host, path = proxy_match.group('host'), proxy_match.group(
                'path')
            proxy_request.headers['Host'] = host
            proxy_request.path = \
                proxy_request.path.replace(f'/{location}',
                                           (path if path else '') +
                                           ('/' if not location else ''),
                                           1)
            return proxy_request
    return None


def get_proxy_response(proxy_request: Request, timeout: float) -> Response:
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.settimeout(5)
    try:
        proxy.connect(proxy_request.host)
        proxy.sendall(bytes(proxy_request))
        raw_proxy_response = receive_all(proxy, timeout)
        response = Response().parse(raw_proxy_response)
    except socket.error:
        response = Response(code=404)
    finally:
        proxy.close()
        return response
