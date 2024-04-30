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


class Charger:
    """Charger class

        possible states:
            idle
            validating
            charging
            disconnected

        possible events:
            connect: idle -> validating
            ok: validating -> charging
            error: validating -> idle
            done_charging: charging -> done_charging
            still_charging: charging -> charging
            disconnect: done_charging -> idle

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

    # Config setter and getter
    def set_config(self, new_config):
        self.config.update(new_config)

    def get_config(self):
        return self.config

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

        if (Id == True) and (name == True) and (email == True):
            #return Id and name and USERS[0]['valid_payment'] and email and True
            return True
        else:
            #return Id and name and USERS[0]['valid_payment'] and email and False
            return False

    def check_user_transition(self):
        if Charger.check_user(self):
            self.stm.send('valid_user')
        else:
            self.stm.send('invalid_user')

    def invalid_error(self):
        print('not valid user')

    def stop_charging(self):
        print('charging done')

    def done(self):
        self.stm.terminate()

    def charge(self):
        max_speed = INFO['max_speed']

        while (self.current_charge < MAX_CHARGE_PERCENTAGE):
            self.current_charge += max_speed
            print(f"You are given {max_speed} electricity%")

        if self.current_charge >= MAX_CHARGE_PERCENTAGE:
            print("You are currently at your preferred charge level.")
            self.stm.send('done_charging')

    def build_message(self) -> dict:
        if self.stm.state == 'charging':
            return {'status': 'charging', 'charging_speed': self.config['CHARGING_SPEED']}

        else:
            return {'status': 'idle'}

    def receive_message(self, message: dict):
        if INFO['status'] == 'connected':
            self.max_speed = message.get('max_speed', 1)
            # ...
            self.stm.send('connect')

        if message['status'] == 'charging':
            current_charge = message.get('current_charge', 0)
            self.stm.send('still_charging')
        # kan ha to tilstander, connect og charging


charger = Charger({
    'charging_speed': CHARGING_SPEED,
    'max_charge_percentage': MAX_CHARGE_PERCENTAGE,
})


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


@app.route('/', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        # Update configuration parameters
        data = request.get_json()
        charger.set_config(data)
        return jsonify({
            "message": "Configuration updated",
            "new_config": charger.get_config()
        }), 200
    elif request.method == 'GET':
        # Retrieve current configuration parameters
        return jsonify(charger.get_config()), 200


def start_flask():
    app.run(port=5001, debug=True, host='0.0.0.0')


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
            charger.receive_message(json.loads(initial_data.decode()))
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
