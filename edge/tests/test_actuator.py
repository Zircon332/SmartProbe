# This file is used for manual control over actuators for testing purposes
# using console input in the format "[WP][01]"
# P - pest
# W - water
# 0 - off
# 1 - on

import socket
from threading import Thread
class ThreadedClient(Thread):
    def __init__(self, socket, addr):
        self._addr = addr
        self._socket = socket
        self._stop_flag = False

        Thread.__init__(self)

    def run(self):
        while True:
            if self._stop_flag:
                break

            msg = input("Actuator Control: \n")
            self.send(msg);
            
    def send(self,msg):
        encoded_msg = msg.encode()
        print("Sending message...");
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
            
            # actuator init states
            thread.send("P0") 
            thread.send("W0")

            threads.append(thread)

    except KeyboardInterrupt:
        for t in threads:
            t.stop()
            t.join()

if __name__ == "__main__":
    main()
