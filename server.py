from config import Config
from socket import socket, AF_INET, SOCK_STREAM
import concurrent.futures
from proxy_passer import ProxyPasser


class Server:
    config = Config()

    def start(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            with socket(AF_INET, SOCK_STREAM) as server:
                server.bind((self.config.host, self.config.port))
                server.listen()
                while 1:
                    print('chtozh...')
                    client, address = server.accept()
                    print(address, 'connected')
                    executor.submit(ProxyPasser(client, self.config.proxy_host, self.config.proxy_port).run)
