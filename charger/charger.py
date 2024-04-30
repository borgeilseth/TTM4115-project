from flask import Flask, request, jsonify
from stmpy import Machine, Driver
import threading
import time
from config import *
import json
import socket


app = Flask(__name__)


class Charger:
    """Charger class

        possible states:
            idle
            validating
            charging
            disconnected

        possible events:
            connect: idle -> validating
            valid_user: validating -> charging
            invalid_user: validating -> idle
            done_charging: charging -> disconnected
            still_charging: charging -> charging
            disconnect: disconnected -> idle

        incoming messages:
            connect
            charging

        outgoing messages:
            charging
            disconnect
    """

    config = {}

    def __init__(self, initial_config):
        self.config = initial_config

    def set_config(self, new_config):
        self.config.update(new_config)
        self.config['charging_speed'] = min(
            self.config['max_charging_speed'],
            self.config['selected_charging_speed']
        )

    def check_user(self):
        """Check user"""
        if not self.config['allow_charging']:
            return False

        if not self.config['id'] in self.config['allowed_cars']:
            return False

        return True

    def check_user_transition(self):
        if self.check_user():
            self.stm.send('valid_user')
        else:
            self.stm.send('invalid_user')

    def invalid_error(self):
        print('not valid user')

    def stop_charging(self):
        print('charging done')

    def done(self):
        print('disconnected')
        pass

    def charge(self):
        max_charging_level = round(
            self.config['max_charge_percentage'] *
            self.config['capacity'] / 100
        )

        if self.config['current_charge'] >= max_charging_level:
            self.stm.send('done_charging')
            return

        if max_charging_level - self.config['current_charge'] < self.config['charging_speed']:
            self.config['charging_speed'] = max_charging_level - \
                self.config['current_charge']
            print(f"Charging speed adjusted to {
                  self.config['charging_speed']}")
            return

    def build_message(self) -> dict:
        if self.stm.state == 'charging':
            return {
                'status': 'charging',
                'charging_speed': self.config['charging_speed']
            }

        else:
            return {'status': self.stm.state}

    def receive_message(self, message: dict):
        if message['status'] == 'connect':
            self.set_config({
                'id': message.get('id', 0),
                'max_charging_speed': message.get('max_charging_speed', 0),
                'current_charge': message.get('current_charge', 0),
                'capacity': message.get('capacity', 0),
            })
            print(json.dumps(self.config, indent=4))
            self.stm.send('connect')

        if message['status'] == 'charging':
            self.set_config({
                'current_charge': message.get('current_charge', 0),
                'capacity': message.get('capacity', 0)
            })
            print(json.dumps(self.config, indent=4))
            self.stm.send('still_charging')


charger = Charger(CONFIG)


# Transitions
t0 = {
    'trigger': '',
    'source': 'initial',
    'target': 'idle',
}

# validate
t1 = {
    'trigger': 'connect',
    'source': 'idle',
    'target': 'validating',
    'effect': 'check_user_transition',
}

# error
t2 = {
    'trigger': 'invalid_user',
    'source': 'validating',
    'target': 'disconnected',
    'effect': 'invalid_error',
}

# start charging
t3 = {
    'trigger': 'valid_user',
    'source': 'validating',
    'target': 'charging',
    'effect': 'charge',
}

# loop transition
t4 = {
    'trigger': 'still_charging',
    'source': 'charging',
    'target': 'charging',
    'effect': 'charge',
}

# done charging
t5 = {
    'trigger': 'done_charging',
    'source': 'charging',
    'target': 'disconnected',
    'effect': 'stop_charging',
}

# disconnected, back to idle
t6 = {
    'trigger': 'disconnect',
    'source': 'disconnected',
    'target': 'idle',
    'effect': 'done',
}

machine = Machine(name='charger', transitions=[
    t0, t1, t2, t3, t4, t5, t6], obj=charger)
charger.stm = machine

driver = Driver()
driver.add_machine(machine)
driver.start()


"""Networking server for handling communication with the car.

The server listens for incoming connections from the car and sends
periodic messages with the current charging speed to the car.

The server also receives from the user and updates the configuration
parameters accordingly.
"""


@ app.route('/', methods=['GET', 'POST'])
def config():
    global charger
    if request.method == 'POST':
        # Update configuration parameters
        data = request.get_json()
        charger.set_config(data)
        return jsonify({
            "message": "Configuration updated",
            "new_config": charger.config
        }), 200
    elif request.method == 'GET':
        # Retrieve current configuration parameters
        return jsonify(charger.config), 200


def start_flask():
    app.run(port=5001, debug=False, host='0.0.0.0')


def server_socket_setup(port=65439):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', port))
    server.listen(1)
    print(f"Socket server listening on port {port}")
    return server


def handle_client_connection(client_socket):
    global charger
    try:
        initial_data = client_socket.recv(1024)
        if initial_data:
            data = json.loads(initial_data.decode())
            charger.receive_message(data)
            print("Received initial message from client:\n", data)
        else:
            print("No initial data received; connection will be closed.")
            return

        def send_periodic_messages():
            while True:
                try:
                    message = charger.build_message()
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
            recieved_message = json.loads(response.decode())
            print("Received from client:", recieved_message)
            charger.receive_message(recieved_message)

    finally:
        client_socket.close()
        print("Connection closed.")
        charger.stm.send('disconnect')


def run_socket_server():
    server = server_socket_setup()
    while True:
        print("Waiting for a new client...")
        client_socket, addr = server.accept()
        print(f"Connected to {addr}")
        handle_client_connection(client_socket)


if __name__ == '__main__':
    threading.Thread(target=run_socket_server).start()
    start_flask()
