import socket
import psutil
import time
from sense_hat import SenseHat

from config import *

def check_connection():
    return "eth0" in psutil.net_if_stats() and psutil.net_if_stats()['eth0'].isup

server_ip = CHARGER_IP
server_port = CHARGER_PORT

client_socket = None

sense = SenseHat()

def connect_to_server():
    global client_socket
    while check_connection():
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))
            print("Connected to server")
            return
        except socket.error as e:
            print("Failed to connect to server, retrying:", e)
            time.sleep(1)
            if client_socket:
                client_socket.close()
                client_socket = None

try:
    while True:
        if check_connection():
            if client_socket is None:
                connect_to_server()

            sense.clear(0, 255, 0)
            if client_socket:
                try:
                    message = "Hello from the client!"
                    client_socket.sendall(message.encode())
                    print("Message sent:", message)
                    # Receive response from the server
                    response = client_socket.recv(1024).decode()
                    print("Received from server:", response)
                except socket.error:
                    print("Connection lost. Reconnecting...")
                    client_socket.close()
                    client_socket = None
                    connect_to_server()
        else:
            if client_socket:
                print("Ethernet Disconnected")
                client_socket.close()
                client_socket = None
                sense.clear(255, 0, 0)

                
        time.sleep(1)
except KeyboardInterrupt:
    if client_socket:
        client_socket.close()
    sense.clear()
    print("Client terminated")
