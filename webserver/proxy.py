import copy
import re
import socket
from select import select

from webserver.http_message import Request, Response

PROXY_REGEX = re.compile(r'(https?://)?(www\.)?(?P<host>[^/]*)(?P<path>/.*)?')


def try_get_proxy_response_and_send_to_client(client: socket,
                                              request: Request,
                                              servers: dict)\
        -> Response or None:
    """
    Try to proxy request and return it, otherwise return None.
    """
    response = None
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
            proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                proxy.connect(proxy_request.host)
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
                            if sock == client:
                                proxy_data += data
                            else:
                                client_data += data

                        for sock in output_ready:
                            if sock == client:
                                if client_data:
                                    bytes_written = client.send(client_data)
                                    if response:
                                        response.headers[
                                            'Content-Length'] += bytes_written
                                    else:
                                        response = Response().\
                                            parse(client_data)
                                    client_data = client_data[bytes_written:]

                            elif proxy_data:
                                bytes_written = proxy.send(proxy_data)
                                proxy_data = proxy_data[bytes_written:]
                    else:
                        break
            except ValueError as e:
                response = Response(code=413)
                print(
                    f"{type(e).__name__} at line {e.__traceback__.tb_lineno} "
                    f"of {__file__}: {e}")
            except Exception as e:
                response = Response(code=502)
                print(
                    f"{type(e).__name__} at line {e.__traceback__.tb_lineno} "
                    f"of {__file__}: {e}")
            finally:
                proxy.close()
                return response
    return None
