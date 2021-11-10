from awscrt import mqtt
import json
import socket
import threading
import uuid

from smartprobe import s3_handler, actuator

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

            sprayer = sprinkler = None
            node_id, moisture, temperature, image = self._buffer.process()

            # Generate and send actuator output
            if moisture is not None and temperature is not None:
                sprinkler = actuator.generate_sprinkler_output(moisture, temperature, 0)
                print("M : " + str(moisture))
                print("Sprinkler : " + sprinkler)

            if image is not None:
                sprayer = actuator.generate_sprayer_output(image)

            if sprinkler is not None:
                self._send(sprinkler)

            if sprayer is not None:
                self._send(sprayer)

            # Generate new node_id and send to MCU
            if node_id == "None":
                # Generate unique ID
                new_id = str(uuid.uuid4())
                self._send("I" + new_id)

            # Upload data to cloud if node_id exists
            elif node_id is not None:
                print(node_id)

                # Upload data to cloud
                if moisture is not None or temperature is not None:
                    body = {
                        "moisture": moisture,
                        "temperature": temperature
                    }

                    print(body)

                    self._mqtt_conn.publish(
                        topic="smartprobe/{}/sensors/data".format(node_id),
                        payload=json.dumps(body),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                        )

                if image is not None:
                    filename = "{}.bmp".format(node_id)

                    print("Uploading image...")
                    s3_handler.upload(image, filename)
                    print("Uploaded.")

                    # Save into local file for checking
                    with open("temp.bmp", "wb") as f:
                        f.write(image)

                if sprinkler is not None or sprayer is not None:
                    body = {
                        "sprinkler": sprinkler,
                        "sprayer": sprayer
                    }

                    print(body)

                    self._mqtt_conn.publish(
                        topic="smartprobe/{}/actions".format(node_id),
                        payload=json.dumps(body),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                        )

    def stop(self):
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()
        self._stop_flag = True

    def _send(self, msg):
        print("Sending message...")
        encoded_msg = msg.encode()

        try:
            self._socket.sendall(encoded_msg)
        except socket.error: #Connection closed
            print("Error occured while writing to client.")
        except Exception as e:
            print(e)

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
            node_id, moisture, temperature, image = self._convert(latest)
        else:
            node_id = moisture = temperature = image = None

        return node_id, moisture, temperature, image

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
        node_id = moisture = temperature = image = None
        values = data.split(b"!#)%@#^#$]")

        for v in values:
            identifier = v[0]

            if identifier == 73:
                node_id = v[1:].decode()

            elif identifier == 77: # Letter "M" for moisture
                moisture = int(v[1:].decode())

            elif identifier == 84: # Letter "T" for temperature
                temperature = float(v[1:].decode())

            elif identifier == 67: # Letter "C" for camera
                image = v[1:]

        return node_id, moisture, temperature, image
