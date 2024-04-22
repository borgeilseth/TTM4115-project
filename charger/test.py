import socket
import psutil
import time

from config import *

def check_connection():
    return "eth0" in psutil.net_if_stats() and psutil.net_if_stats()['eth0'].isup

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((CHARGER_IP, CHARGER_PORT))
server_socket.listen(1)
print(f"Server listening on {CHARGER_IP}:{CHARGER_PORT}")

try:
    while True:
        connected = check_connection()
        if connected:
            print("Ethernet Connected")
            connection, addr = server_socket.accept()
            print(f"Connected to {addr}")
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                print("Received:", data.decode())
            connection.close()
            print("Connection closed")
        else:
            print("Ethernet Disconnected")
        time.sleep(1)
except KeyboardInterrupt:
    server_socket.close()
