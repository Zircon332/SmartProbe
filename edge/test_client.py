import socket

client = socket.socket()

with client:
    client.connect(("localhost", 12345))

    while True:
        msg = input(">>> ")
        client.send(msg.encode("utf-8"))

        msg = client.recv(1024)
        print("ECHO: ", msg)
