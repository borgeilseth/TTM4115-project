import socket
import json
import time
from config import *
import threading
# from sense_hat import SenseHat

# sense = SenseHat()

dissalowed = False


class Car():
    """Car class for handling car logic and state

    Can have three states:
        idle
            When the car is not connected to the charger
        charging
            When the car is connected to the charger
    """

    state = "idle"

    def __init__(self, initial_charge=INITIAL_CHARGE):
        self.current_charge = initial_charge

    def build_connect_message(self) -> dict:
        return {
            "status": "connect",
            "id": '1',
            "max_charging_speed": MAX_CHARGING_RATE,
            "current_charge": self.current_charge,
            "capacity": MAX_CHARGE_CAPACITY,
        }

    def build_charging_message(self) -> dict:
        return {
            "status": "charging",
            "current_charge": self.current_charge,
            "capacity": MAX_CHARGE_CAPACITY
        }

    def refresh_sense_led(self):
        global sense
        # Change the sense led color according to the charge and state

        pass

    def update_charge(self, change):
        self.current_charge += change
        if self.current_charge >= MAX_CHARGE_CAPACITY:
            self.current_charge = MAX_CHARGE_CAPACITY
        elif self.current_charge < 0:
            self.current_charge = 0
        self.refresh_sense_led()

    def set_state(self, state):
        self.state = state
        self.refresh_sense_led()

    def receive_message(self, message: dict):
        print(f"Received message: {message}")
        if not message:
            return True
        elif message["status"] == "charging":
            self.update_charge(message.get("charging_speed", 0))
            self.set_state("charging")
            print(f"Current charge: {self.current_charge}, "
                  f"State: {self.state}")
            return True
        elif message["status"] == "disconnect":
            threading.Thread(target=dissalow_timeouts).start()
            return False
        return True


car = Car()


def dissalow_timeouts():
    global dissalowed
    dissalowed = True
    time.sleep(10)
    dissalowed = False


def send_message(sock, message):
    try:
        serialized_message = json.dumps(message)
        sock.sendall(serialized_message.encode())
    except json.JSONDecodeError:
        print("Failed to serialize message")


def start_client(server_host=CHARGER_IP, server_port=CHARGER_PORT):
    global dissalowed
    while True:
        print(f"Current charge: {car.current_charge}, State: {car.state}")

        if not dissalowed:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

                    sock.connect((server_host, server_port))
                    # print("Charging")

                    send_message(sock, car.build_connect_message())
                    while True:
                        data = sock.recv(1024)
                        if not data:
                            break
                        try:
                            received_message = json.loads(data.decode())
                            if not car.receive_message(received_message):
                                break

                            send_message(
                                sock, car.build_charging_message())
                        except json.JSONDecodeError:
                            print("Failed to decode message")
            except socket.error:
                pass

        car.set_state("idle")
        car.update_charge(DISCHARGE_RATE)
        time.sleep(1)


if __name__ == "__main__":
    # start_client(CHARGER_IP, CHARGER_PORT)
    start_client()
