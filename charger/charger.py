from stmpy import Machine, Driver
import random
import re
import time
from config import *
import json
import socket


class Charger:

    current_charge = None

    """
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

    def check_user(self):
        "Check user"

        if re.match(r'^\d{4}-\d{4}-\d{4}$', USERS[0]['UUID']) is not None:
            Id = True
        else:
            Id = False

        if re.match(r'^[A-Za-z]+$', USERS[0]['name']) is not None:
            name = True
        else:
            name = False

        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', USERS[0]['email']) is not None:
            email = True
        else:
            email = False

        return (Id and name and USERS[0]['valid_payment'] and email)

    def check_user_transition(self):
        if Charger.check_user(self):
            self.stm.send("valid_user")
        else:
            self.stm.send("invalid_user")

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
            print(f"You are now at {current_charge}%")

        if current_charge >= MAX_CHARGE_PERCENTAGE:
            print("You are currently at your preferred charge level.")

    def build_message(self) -> dict:
        if self.stm.state() == "charging":
            return {
                "status": "charging",
                "charging_speed": self.charge_speed
            }

        if self.stm.state() == "disconnect":
            return {
                "status": "disconnect"
            }

    def receive_message(self, message: dict):
        print("Received from car: \n \t", message)
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
    'effect': 'check_user_transition'
}

# error
t2 = {
    'trigger': 'invalid_user',
    'source': 'validating',
    'target': 'disconnect',
    'effect': 'invalid_error'
}

# start charging
t3 = {
    'trigger': 'valid_user',
    'source': 'validating',
    'target': 'charging',
    'effect': 'check_settings; charge'
}

# loop transition
t4 = {
    'trigger': 'still_charging',
    'source': 'charging',
    'target': 'charging',
    'effect': 'charge'
}

# done charging
t5 = {
    'trigger': 'done_charging',
    'source': 'charging',
    'target': 'disconnect',
    'effect': 'stop_charging'
}

# disconnected, back to idle
t6 = {
    'trigger': 'disonnect',
    'source': 'disconnect',
    'target': 'idle',
    'effect': 'done'
}


def send_message(s, message):
    serialized_message = json.dumps(message)
    s.sendall(serialized_message.encode())


def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server started and listening on {host}:{port}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                received_message = json.loads(data.decode())
                charger.receive_message(received_message)
                time.sleep(1)
                response = charger.build_message()
                send_message(conn, response)


# State machine for the charger
charger = Charger()

machine = Machine(name='charger', transitions=[
                  t0, t1, t2, t3, t4, t5, t6], obj=charger)
charger.stm = machine

driver = Driver()
driver.add_machine(machine)
driver.start()


if __name__ == "__main__":
    start_server()
