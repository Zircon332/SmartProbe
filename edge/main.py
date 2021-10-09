import socket
from threading import Thread

class Buffer():
    def __init__(self):
        self._data = ""

    def append(self, msg):
        self._data += msg

    def process(self):
        latest = None

        # Retrieve latest piece of data
        while True:
            data = self._extract()

            if not data:
                break

            latest = data

        if latest:
            moisture, temperature = self._convert(latest)
        else:
            moisture = temperature = None

        return moisture, temperature

    def clear(self):
        self._data = ""

    def _extract(self):
        i = self._data.find("\r\n")

        # Complete piece of data does not exist
        if i == -1:
            return None

        # Retrieve first complete piece
        data = self._data[:i]

        # Cut away extracted piece so it does not appear in future extractions
        self._data = self._data[i+2:]

        return data

    def _convert(self, data):
        moisture = temperature = None
        values = data.split("|")

        for v in values:
            identifier = v[0]

            if identifier == "M":
                moisture = int(v[1:])

            elif identifier == "T":
                temperature = float(v[1:])

        return moisture, temperature

class ThreadedClient(Thread):
    def __init__(self, socket, addr):
        self._addr = addr
        self._buffer = Buffer()
        self._socket = socket
        self._stop_flag = False

        Thread.__init__(self)

    def run(self):
        while True:
            if self._stop_flag:
                break

            msg = self._socket.recv(1024)

            # Closing clients send 0 bytes
            if msg == b"":
                print(f"Client closed at {self._addr}.")
                self.stop()
                break

            # Append data to buffer, in case of split data
            self._buffer.append(msg.decode())

            moisture, temperature = self._buffer.process()

            print("Moisture:", moisture)
            print("Temperature:", temperature)
            print("")
            
    
    def send(self,msg):
        encoded_msg = msg.encode()
        print("sending message");
        try:
            self._socket.sendall(encoded_msg)
        except socket.error: #Connection closed
            print("Error occured while writing to client.")
        except Exception as e:
            print(e)

    def stop(self):
        self._socket.close()
        self._stop_flag = True

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", 12345))
    server.listen(5) # Listen to X number of clients

    threads = []

    try:
        while True:
            print("Waiting for clients...")
            client, addr = server.accept()

            print(f"Client detected at {addr}, starting separate thread...")
            thread = ThreadedClient(client, addr)
            thread.start()
            
            thread.send("P0") # W0 = Water Sprinkler OFF

            threads.append(thread)

    except KeyboardInterrupt:
        for t in threads:
            t.stop()
            t.join()

if __name__ == "__main__":
    main()
