import socket
import psutil
import time

def check_connection():
    return "eth0" in psutil.net_if_stats() and psutil.net_if_stats()['eth0'].isup

server_ip = '192.168.1.1'
server_port = 12345

try:
    while True:
        connected = check_connection()
        if connected:
            print("Ethernet Connected")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((server_ip, server_port))
                client_socket.sendall("Hello from the client!".encode())
                client_socket.close()
            print("Message sent")
        else:
            print("Ethernet Disconnected")
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated")
