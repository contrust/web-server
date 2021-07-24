import logging
from webserver.config import Config
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import concurrent.futures
from webserver.client_handler import ClientHandler
from webserver.timed_lru_cache import TimedLruCache


class Server:
    def __init__(self, config: Config):
        self.config = config
        self.cache = TimedLruCache(config.open_file_cache_size, config.open_file_cache_inactive_time)
        logging.basicConfig(filename=config.log_file,
                            level=logging.DEBUG,
                            format='%(message)s')

    def run(self) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            with socket(AF_INET, SOCK_STREAM) as server:
                server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                server.bind((self.config.hostname, self.config.port))
                server.listen()
                while 1:
                    client, address = server.accept()
                    executor.submit(ClientHandler(client=client,
                                                  config=self.config,
                                                  cache=self.cache).run)
