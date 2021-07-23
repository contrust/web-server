import socket
from select import select


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
            except BlockingIOError:
                return b''.join(total_data)
        return b'timeout'

    def write(self, data: bytes) -> None:
        self.socket.sendall(data)
