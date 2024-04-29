import socket
import json
import time
from config import *


class Car():
    state = "idle"  # possible values: idle, charging

    def __init__(self, initial_charge=INITIAL_CHARGE):
        self.current_charge = initial_charge

    def build_connect_message(self) -> dict:
        return {
            "status": "connect",
            # ...
            "max_charging_speed": MAX_CHARGING_SPEED,
            "current_charge": self.current_charge,
        }

    def build_charging_message(self) -> dict:
        return {
            "status": "charging",
            "current_charge": self.current_charge,
            "capacity": MAX_CHARGE_CAPACITY
        }

    def update_charge(self, charging_speed):
        self.current_charge += charging_speed
        if self.current_charge >= MAX_CHARGE_CAPACITY:
            self.current_charge = MAX_CHARGE_CAPACITY
            self.state = "idle"
        else:
            self.state = "charging"

    def receive_message(self, message: dict):
        if message["status"] == "charging":
            self.update_charge(message.get("charging_speed", 0))
        elif message["status"] == "disconnect":
            self.state = "idle"


def send_message(sock, message):
    try:
        serialized_message = json.dumps(message)
        sock.sendall(serialized_message.encode())
    except json.JSONDecodeError:
        print("Failed to serialize message")


def start_client(server_host='127.0.0.1', server_port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((server_host, server_port))
            print("Connected to server")

            send_message(sock, car.build_connect_message())
            while car.state != "idle":
                data = sock.recv(1024)
                if not data:
                    break
                try:
                    received_message = json.loads(data.decode())
                    car.receive_message(received_message)
                    send_message(sock, car.build_charging_message())
                except json.JSONDecodeError:
                    print("Failed to decode message")
        except socket.error as e:
            print(f"Socket error: {e}")


car = Car()

if __name__ == "__main__":
    # start_client(CHARGER_IP, CHARGER_PORT)
    start_client()
