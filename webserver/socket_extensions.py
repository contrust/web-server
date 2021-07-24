from select import select


def receive_all(sock, timeout) -> bytes:
    total_data = []
    sock.setblocking(0)
    ready = select([sock], [], [], timeout)
    while ready[0]:
        try:
            data = sock.recv(8192)
            total_data.append(data)
            if not data:
                break
        except BlockingIOError:
            return b''.join(total_data)
    return b''
