from awscrt import mqtt
import json
import socket
import threading

from smartprobe import s3_handler

class ThreadedClient(threading.Thread):
    def __init__(self, socket, addr, mqtt_conn):
        self._addr = addr
        self._buffer = Buffer()
        self._mqtt_conn = mqtt_conn
        self._socket = socket
        self._stop_flag = False

        threading.Thread.__init__(self)

    def run(self):
        while True:
            if self._stop_flag:
                break

            msg = self._socket.recv(4096)

            # Closing clients send 0 bytes
            if msg == b"":
                print(f"Client closed at {self._addr}.")
                self.stop()
                break

            # Append data to buffer, in case of split data
            self._buffer.append(msg)

            moisture, temperature, image = self._buffer.process()

            if moisture is not None or temperature is not None:
                body = {
                    "moisture": moisture,
                    "temperature": temperature
                }

                print(body)

                self._mqtt_conn.publish(
                    topic="smartprobe/abc/sensors/data",
                    payload=json.dumps(body),
                    qos=mqtt.QoS.AT_LEAST_ONCE
                    )

            if image is not None:
                with open("temp.bmp", "wb") as f:
                    f.write(image)

                print("Uploading image...")
                s3_handler.upload(image, "temp.bmp")
                print("Uploaded.")

    def send(self, msg):
        print("Sending message...")
        encoded_msg = msg.encode()

        try:
            self._socket.sendall(encoded_msg)
        except socket.error: #Connection closed
            print("Error occured while writing to client.")
        except Exception as e:
            print(e)

    def stop(self):
        self._socket.shutdown()
        self._socket.close()
        self._stop_flag = True

class Buffer():
    def __init__(self):
        self._data = bytearray()

    def append(self, msg):
        self._data += bytearray(msg)

    def process(self):
        latest = None

        # Retrieve latest piece of data
        while True:
            data = self._extract()

            if data == None:
                break

            latest = data

        if latest:
            moisture, temperature, image = self._convert(latest)
        else:
            moisture = temperature = image = None

        return moisture, temperature, image

    def clear(self):
        self._data = bytearray()

    def _extract(self):
        i = self._data.find(b"\r\n")

        # Complete piece of data does not exist
        if i == -1:
            return None

        # Retrieve first complete piece
        data = self._data[:i]

        # Cut away extracted piece so it does not appear in future extractions
        self._data = self._data[i+2:]

        return data

    def _convert(self, data):
        moisture = temperature = image = None
        values = data.split(b"!#)%@#^#$]")

        for v in values:
            identifier = v[0]

            if identifier == 77: # Letter "M" for moisture
                moisture = int(v[1:].decode())

            elif identifier == 84: # Letter "T" for temperature
                temperature = float(v[1:].decode())

            elif identifier == 67: # Letter "C" for camera
                image = v[1:]

        return moisture, temperature, image
