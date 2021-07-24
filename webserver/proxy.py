import copy
import re

from webserver.http_message import Request

PROXY_REGEX = re.compile(r'(https?://)?(www\.)?(?P<host>[^/]*)(?P<path>/.*)?')


def try_get_proxy_request(request: Request, proxy_pass: dict) \
        -> Request or None:
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
