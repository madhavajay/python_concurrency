import gevent
from gevent.server import StreamServer
from gevent import socket
import gipc
import time
import sys


PORT = 1337
N_CLIENTS = 1000
MSG = "HELLO\n"


def serve(sock, addr):
    f = sock.makefile(mode='rw')
    f.write(f.readline())
    f.flush()
    f.close()


def server():
    ss = StreamServer(('localhost', PORT), serve).serve_forever()


def clientprocess():
    t0 = time.time()
    clients = [gevent.spawn(client) for _ in range(N_CLIENTS)]
    gevent.joinall(clients)
    duration = time.time() - t0
    print('%s clients served within %.2f s.' % (N_CLIENTS, duration))


def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', PORT))
    f = sock.makefile(mode='wr')
    f.write(MSG)
    f.flush()
    assert f.readline() == MSG
    f.close()


if __name__ == "__main__":
    s = gevent.spawn(server)
    c = gipc.start_process(clientprocess)
    c.join()
    s.kill()
    s.join()
