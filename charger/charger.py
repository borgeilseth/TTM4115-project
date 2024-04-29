from flask import Flask, request, jsonify
from stmpy import Machine, Driver
import random
import threading
import re
import time
from config import *
import json
import socket


app = Flask(__name__)

"""Global variables"""
config_params = {
    'max_charge_percentage': MAX_CHARGE_PERCENTAGE,
    'charging_speed': CHARGING_SPEED,
    'users': USERS,
    # TODO: Add more parameters if needed
}


class Charger:
    """Charger class

        possible states:
            idle
            validating
            charging
            done_charging

        possible events:
            connect: idle -> validating
            ok: validating -> charging
            error: validating -> idle
            done_charging: charging -> done_charging
            disconnect: done_charging -> idle

        incoming messages:
            connect
            charging

        outgoing messages:
            charging
            disconnect
    """

    current_charge = 0

    def check_user(self):
        """Check user"""

        if re.match(r'^\d{4}-\d{4}-\d{4}$', USERS[0]['UUID']) is not None:
            Id = True
        else:
            Id = False

        if re.match(r"^[A-Za-z]+$", USERS[0]['name']) is not None:
            name = True
        else:
            name = False

        if (
            re.match(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", USERS[0]['email']
            )
            is not None
        ):
            email = True
        else:
            email = False

        return Id and name and USERS[0]['valid_payment'] and email

    def check_user_transition(self):
        if Charger.check_user(self):
            self.stm.send('valid_user')
        else:
            self.stm.send('invalid_user')

    def check_settings(self):
        print('checking settings')

    def invalid_error(self):
        print('not valid user')

    def stop_charging(self):
        print('charging done')

    def on_idle(self):
        print('Idling')

    def done(self):
        self.stm.terminate()

    def charge(self):
        max_speed = INFO['max_speed']

        if self.current_charge < MAX_CHARGE_PERCENTAGE:
            self.current_charge += max_speed
            print(f"You are now at {self.current_charge}%")

        if self.current_charge >= MAX_CHARGE_PERCENTAGE:
            print("You are currently at your preferred charge level.")

    def build_message(self) -> dict:
        global config_params
        print(config_params)
        return {
            'status': self.stm.state,
            'charging_speed': config_params.get('charging_speed', 0),
        }

        if self.stm.state == 'charging':
            return {'status': 'charging', 'charging_speed': self.charge_speed}

        if self.stm.state == 'disconnect':
            return {'status': 'disconnect'}

    def receive_message(self, message: dict):
        if INFO['status'] == 'connect':
            self.max_speed = message.get('max_speed', 1)
            # ...
            self.stm.send('connect')

        if message['status'] == 'charging':
            current_charge = message.get('current_charge', 0)
            self.stm.send('still_charging')
        # kan ha to tilstander, connect og charging


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
    'target': 'disconnect',
    'effect': 'invalid_error',
}

# start charging
t3 = {
    'trigger': 'valid_user',
    'source': 'validating',
    'target': 'charging',
    'effect': 'check_settings; charge',
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
    'target': 'disconnect',
    'effect': 'stop_charging',
}

# disconnected, back to idle
t6 = {
    'trigger': 'disonnect',
    'source': 'disconnect',
    'target': 'idle',
    'effect': 'done',
}

# State machine for the charger.
charger = Charger()

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


@app.route('/', methods=['GET', 'POST'])
def config():
    global config_params
    if request.method == 'POST':
        # Update configuration parameters
        data = request.get_json()
        config_params.update(data)
        return jsonify({"message": "Configuration updated", "new_config": config_params}), 200
    elif request.method == 'GET':
        # Retrieve current configuration parameters
        return jsonify(config_params), 200


def start_flask():
    app.run(port=5001, debug=True)


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
