import threading

from config import Config
from socket import socket, AF_INET, SOCK_STREAM
import concurrent.futures
from client import Client


class Server:
    config = Config()

    def start(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            with socket(AF_INET, SOCK_STREAM) as server:
                server.bind((self.config.host, self.config.port))
                server.listen()
                while 1:
                    print('trying to find new client...')
                    client, address = server.accept()
                    print(address, 'connected')
                    print(f'{threading.activeCount()} threads are active')
                    executor.submit(Client(client).run)
