import copy
import re
import socket
import logging
from select import select

from webserver.http_message import Request, Response

PROXY_REGEX = re.compile(r'(https?://)?(www\.)?(?P<host>[^/]*)(?P<path>/.*)?')


def try_get_proxy_request(request: Request,
                          servers: dict) -> Request:
    """
    Try to get proxy request.
    """
    proxy_pass = {}
    if 'Host' in request.headers and request.headers['Host'] in servers:
        proxy_pass = servers[request.headers['Host']]['proxy_pass']
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


def try_get_and_send_proxy_response(client: socket,
                                    request: Request,
                                    servers: dict) -> Response:
    """
    Get response from proxy and send it to the client.
    """
    proxy_request = try_get_proxy_request(request, servers)
    if not proxy_request:
        return None
    response = None
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        proxy.connect(proxy_request.host)
    except (socket.error, socket.gaierror) as e:
        logging.getLogger(request.headers['Host']).exception(e)
        return Response(code=502)
    client.settimeout(0)
    proxy.settimeout(0)
    proxy_data = bytes(proxy_request)
    try:
        proxy.sendall(proxy_data)
    except (socket.error, socket.gaierror) as e:
        logging.getLogger(request.headers['Host']).exception(e)
        proxy.close()
        return Response(code=502)
    ready, _, _ = select([proxy], [], [], 5)
    while ready:
        try:
            data = proxy.recv(8192)
            if response:
                response.headers['Content-Length'] += len(data)
            else:
                try:
                    response = Response().parse(data)
                except ValueError as e:
                    logging.getLogger(
                        request.headers['Host']).exception(e)
                    return Response(code=413)
            try:
                client.sendall(data)
            except socket.error as e:
                logging.getLogger(request.headers['Host']).exception(e)
                return Response(code=400)
            if not data:
                break
        except BlockingIOError:
            return response
    return Response(code=408)
