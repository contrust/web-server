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
    if request.headers['Host'] in servers:
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
    client_data = b''
    proxy_data = bytes(proxy_request)
    while True:
        outputs = []
        if client_data:
            outputs.append(client)
        if proxy_data:
            outputs.append(proxy)

        input_ready, output_ready, _ = select([client, proxy],
                                              outputs, [], 5)

        if input_ready or output_ready:
            for sock in input_ready:
                try:
                    data = sock.recv(8192)
                except BlockingIOError:
                    data = b''
                except socket.error as e:
                    logging.getLogger(request.headers['Host']).exception(e)
                    return Response(code=400)
                if sock == client:
                    proxy_data += data
                else:
                    client_data += data

            for sock in output_ready:
                if sock == client:
                    if client_data:
                        try:
                            bytes_written = client.send(client_data)
                        except socket.error as e:
                            logging.getLogger(
                                request.headers['Host']).exception(e)
                            return Response(code=400)
                        if response:
                            response.headers[
                                'Content-Length'] += bytes_written
                        else:
                            try:
                                response = Response().parse(client_data)
                            except ValueError as e:
                                logging.getLogger(
                                    request.headers['Host']).exception(e)
                                return Response(code=413)
                        client_data = client_data[bytes_written:]

                elif proxy_data:
                    try:
                        bytes_written = proxy.send(proxy_data)
                    except socket.error as e:
                        logging.getLogger(
                            request.headers['Host']).exception(e)
                        return Response(code=502)
                    proxy_data = proxy_data[bytes_written:]
        else:
            break
    proxy.close()
    return response
