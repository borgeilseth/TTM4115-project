import socket
import psutil
import time

from config import *

def check_connection():
    return "eth0" in psutil.net_if_stats() and psutil.net_if_stats()['eth0'].isup

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((CHARGER_IP, CHARGER_PORT))
    server_socket.listen(1)
    print(f"Server listening on {CHARGER_IP}:{CHARGER_PORT}")
    return server_socket

server_socket = None
connection = None

try:
    while True:
        if check_connection():
            if server_socket is None:
                server_socket = start_server()

            if connection is None:
                print("Waiting for a client...")
                connection, addr = server_socket.accept()
                print(f"Connected to {addr}")

            try:
                data = connection.recv(1024)
                if not data:
                    raise ConnectionResetError
                print("Received:", data.decode())
            except ConnectionResetError:
                print("Client disconnected")
                connection.close()
                connection = None
        else:
            if connection:
                connection.close()
                connection = None
            if server_socket:
                server_socket.close()
                server_socket = None
            print("Ethernet Disconnected")
        time.sleep(1)
except KeyboardInterrupt:
    if connection:
        connection.close()
    if server_socket:
        server_socket.close()
    print("Server shutting down")
