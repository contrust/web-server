from config import Config
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import concurrent.futures
from client import Client
from file_handler import FileHandler


class Server:
    def __init__(self, config: Config):
        self.config = config
        self.file_handler = FileHandler(**self.config.__dict__)

    def start(self) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            with socket(AF_INET, SOCK_STREAM) as server:
                server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                server.bind((self.config.host, self.config.port))
                server.listen()
                while 1:
                    client, address = server.accept()
                    executor.submit(Client(client=client,
                                           config=self.config,
                                           file_handler=self.file_handler).run)
