from config import Config
from socket import socket, AF_INET, SOCK_STREAM


class Server:
    config = Config()

    def start(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((self.config.host, self.config.port))
        server_socket.listen()
        while 1:
            client_socket, client_address = server_socket.accept()
            print(client_address)

