import socket
from threading import Thread

class ThreadedClient(Thread):
    def __init__(self, socket, addr):
        self._addr = addr
        self._buffer = ""
        self._socket = socket

        Thread.__init__(self)

    def run(self):
        while True:
            msg = self._socket.recv(1024)

            if msg == b"":
                print(f"Client closed at {self._addr}")
                break

            print(self._addr, ">>", msg)

            self._socket.send(msg)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", 12345))
    server.listen(5) # Listen to X number of clients

    while True:
        print("Waiting for clients...")
        client, addr = server.accept()

        print(f"Client detected at {addr}, starting separate thread...")
        thread = ThreadedClient(client, addr)
        thread.start()
        


if __name__ == "__main__":
    main()
