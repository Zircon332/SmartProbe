from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import json
import os
import sys
import uuid

def begin():
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=os.getenv("THING_ENDPOINT"),
        cert_filepath=os.getenv("CERT_FILE"),
        pri_key_filepath=os.getenv("PRIVATE_KEY_FILE"),
        client_bootstrap=client_bootstrap,
        ca_filepath=os.getenv("CA_FILE"),
        on_connection_interrupted=_on_connection_interrupted,
        on_connection_resumed=_on_connection_resumed,
        client_id=os.getenv("CLIENT_ID") or str(uuid.uuid4()),
        clean_session=False,
        keep_alive_secs=30)

    print("Connecting to {}...".format(os.getenv("THING_ENDPOINT")))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    return mqtt_connection


# Callback when connection is accidentally lost.
def _on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def _on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(_on_resubscribe_complete)


def _on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv()

    mqtt_connection = setup()

    mqtt_connection.publish(
        topic="smartprobe/abc/sensors/data",
        payload=json.dumps({ "message": "Hello world!" }),
        qos=mqtt.QoS.AT_LEAST_ONCE)

    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
