import threading

from config import Config
from socket import socket, AF_INET, SOCK_STREAM
import concurrent.futures
from client import Client
from file_handler import FileHandler


class Server:
    config = Config()
    file_handler = FileHandler()

    def start(self) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            with socket(AF_INET, SOCK_STREAM) as server:
                server.bind((self.config.host, self.config.port))
                server.listen()
                while 1:
                    client, address = server.accept()
                    executor.submit(Client(client, self.file_handler).run)
