import logging
from webserver.config import Config
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import concurrent.futures
from webserver.client import Client
from webserver.file_handler import FileHandler


class Server:
    def __init__(self, config: Config):
        self.config = config
        self.file_handler = FileHandler(config)
        logging.basicConfig(filename=config.log_file,
                            level=logging.DEBUG,
                            format='%(asctime)s %(message)s')

    def run(self) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            with socket(AF_INET, SOCK_STREAM) as server:
                server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                server.bind((self.config.hostname, self.config.port))
                server.listen()
                logging.info(f'{self.config.hostname} launched with {self.config.port} port')
                while 1:
                    client, address = server.accept()
                    executor.submit(Client(client=client,
                                           file_handler=self.file_handler).run)
