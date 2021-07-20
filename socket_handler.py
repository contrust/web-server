from socket import socket
from select import select
import errno


class SocketHandler:
    def __init__(self, sock: socket, timeout: float):
        self.timeout = timeout
        self.socket = sock

    def read(self) -> bytes:
        total_data = []
        self.socket.setblocking(False)
        ready = select([self.socket], [], [], self.timeout)
        while ready[0]:
            try:
                data = self.socket.recv(8192)
                total_data.append(data)
                if not data:
                    break
            except Exception as e:
                if e.errno == errno.EWOULDBLOCK:
                    break
        return b''.join(total_data)

    def write(self, data: bytes) -> None:
        self.socket.sendall(data)
