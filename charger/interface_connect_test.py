from flask import Flask, request, jsonify
import threading
import socket
import time
import json

app = Flask(__name__)

# Configuration parameters stored in a dictionary
config_params = {
    "charging_speed": 22.0,  # in kWh, example parameter
}

# Setup Flask routes for parameter management


@app.route('/', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        # Update configuration parameters
        data = request.get_json()
        config_params.update(data)
        return jsonify({"message": "Configuration updated", "new_config": config_params}), 200
    elif request.method == 'GET':
        # Retrieve current configuration parameters
        return jsonify(config_params), 200


def start_flask():
    app.run(port=5001, debug=False)


def server_socket_setup(port=65439):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(1)
    print(f"Socket server listening on port {port}")
    return server


def handle_client_connection(client_socket):
    try:
        initial_data = client_socket.recv(1024)
        if initial_data:
            print("Received initial message from client:", initial_data.decode())
        else:
            print("No initial data received; connection will be closed.")
            return

        def send_periodic_messages():
            while True:
                try:
                    message = {
                        "time": time.time(),
                        "message": "Server periodic message",
                        "charging_speed": config_params["charging_speed"]
                    }
                    serialized_message = json.dumps(message)
                    client_socket.sendall(serialized_message.encode())
                    time.sleep(1)
                except socket.error:
                    print("Socket error, stopping sender thread.")
                    break

        sender_thread = threading.Thread(target=send_periodic_messages)
        sender_thread.daemon = True
        sender_thread.start()

        while True:
            response = client_socket.recv(1024)
            if not response:
                print("Client disconnected.")
                break
            print("Received from client:", response.decode())

    finally:
        client_socket.close()
        print("Connection closed.")


def run_socket_server():
    server = server_socket_setup()
    while True:
        print("Waiting for a new client...")
        client_socket, addr = server.accept()
        print(f"Connected to {addr}")
        handle_client_connection(client_socket)


if __name__ == "__main__":
    # Run Flask and socket server on different threads
    threading.Thread(target=run_socket_server).start()
    start_flask()
