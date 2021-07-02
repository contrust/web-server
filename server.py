from config import Config
from socket import socket, AF_INET, SOCK_STREAM
import concurrent.futures
from select import select
import errno
from request import Request


class Server:
    config = Config()

    def start(self):
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.config.max_processes) as executor:
            with socket(AF_INET, SOCK_STREAM) as server_socket:
                server_socket.bind((self.config.host, self.config.port))
                server_socket.listen()
                while 1:
                    client_socket, client_address = server_socket.accept()
                    executor.submit(serve, client_socket)


def get_all_client_data(client: socket, timeout=5):
    total_data = []
    client.setblocking(False)
    ready = select([client], [], [], timeout)
    while ready[0]:
        try:
            data = client.recv(8192)
            total_data.append(data)
        except Exception as e:
            if e.errno == errno.EWOULDBLOCK:
                break
    return b''.join(total_data)


def serve(client: socket):
    while data := get_all_client_data(client):
        print(data)
