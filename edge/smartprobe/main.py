import dotenv
import socket

from smartprobe import mqtt_handler, threaded

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", 12345))
    server.listen(5) # Listen to X number of clients

    mqtt_connection = mqtt_handler.begin()

    threads = []

    try:
        while True:
            print("Waiting for clients...")
            client, addr = server.accept()

            print(f"Client detected at {addr}, starting separate thread...")
            thread = threaded.ThreadedClient(
                socket=client,
                addr=addr,
                mqtt_conn=mqtt_connection)
            thread.start()

            threads.append(thread)

    except KeyboardInterrupt:
        print("Stopping threads...")
        for index, t in enumerate(threads):
            t.stop()
            t.join()
            print(f"\tStopped thread {index}.")
        print("Stopped all threads.")

        print("Disconnecting MQTT connection...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected.")

if __name__ == "__main__":
    dotenv.load_dotenv()

    main()
