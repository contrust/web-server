from config import Config
from socket import socket
from select import select
import errno


class SocketHandler:
    def __init__(self, sock: socket):
        self.config = Config()
        self.socket = sock

    def read(self) -> bytes:
        print('start reading..')
        total_data = []
        self.socket.setblocking(False)
        ready = select([self.socket], [], [], self.config.connection_timeout)
        while ready[0]:
            try:
                data = self.socket.recv(8192)
                total_data.append(data)
                if not data:
                    break
            except Exception as e:
                if e.errno == errno.EWOULDBLOCK:
                    break
        print('done reading...')
        return b''.join(total_data)

    def write(self, data: bytes) -> None:
        print('son are you writing?')
        print('yes dad')
        print(data)
        self.socket.sendall(data)
