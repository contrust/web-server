from config import Config
from socket import socket, AF_INET, SOCK_STREAM
import concurrent.futures
import errno
from request import Request


class Server:
    config = Config()

    def start(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((self.config.host, self.config.port))
        server_socket.listen()
        while 1:
            client_socket, client_address = server_socket.accept()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self.get_all_client_data, client_socket)
                return_value = future.result()
                print(Request(return_value).body)

    @staticmethod
    def get_all_client_data(client: socket):
        client.setblocking(False)
        total_data = []
        while 1:
            try:
                data = client.recv(8192)
                total_data.append(data)
            except IOError as e:
                if e.errno == errno.EWOULDBLOCK:
                    break
        return b''.join(total_data)
