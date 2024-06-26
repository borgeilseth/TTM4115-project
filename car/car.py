import socket
import json
import time
import math
from config import *
import threading
from sense_hat import SenseHat


dissalowed = False

car = None

sense = SenseHat()
green = (0, 255, 0)
red = (255, 0, 0)
pink = (255, 0, 255)
black = (0, 0, 0)


class Car():
    """Car class for handling car logic and state

    Can have two states:
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

    def turn_on_led_rows(number_rows):
        number_rows = max(1, min(number_rows, 8))
        for i in range(number_rows):
            for j in range(8):
                sense.set_pixel(j, i, 0, 255, 0)

    def refresh_sense_led(self):
        global sense
        # Change the sense led color according to the charge and state
        if self.state == "idle":
            color = red
        elif self.state == "charging":
            color = green

        sense.clear()
        percentage = self.current_charge/MAX_CHARGE_CAPACITY
        number_of_pixels_on = math.floor(percentage * 64)

        pixels = []
        for i in range(8):
            for j in range(8):
                if i * 8 + j < number_of_pixels_on:
                    pixels.append(color)
                else:
                    pixels.append(black)

        sense.set_pixels(pixels)

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
        global dissalowed
        # print(f"Received message: {message}, dissalowed: {dissalowed}")
        if not message:
            return True
        elif message["status"] == "charging":
            self.update_charge(message.get("charging_speed", 0))
            self.set_state("charging")
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
    global car
    global dissalowed
    while True:

        if not dissalowed:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(2)
                    sock.connect((server_host, server_port))

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


def update_car():
    global car
    global sense

    try:
        while True:
            print(f"Current charge: {car.current_charge}, State: {car.state}")
            if car.state == "idle":
                car.update_charge(DISCHARGE_RATE)
            time.sleep(1)
    except KeyboardInterrupt:
        sense.clear()


if __name__ == "__main__":
    threading.Thread(target=update_car).start()
    start_client()
