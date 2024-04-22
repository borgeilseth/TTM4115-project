import socket
import psutil
import time
import threading

def check_connection():
    return "eth0" in psutil.net_if_stats() and psutil.net_if_stats()['eth0'].isup

def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if data:
                print("Received from server:", data.decode())
        except socket.error:
            print("Lost connection to the server.")
            break

def send_messages(client_socket):
    while True:
        try:
            message = "Hello from client at {}".format(time.ctime())
            client_socket.sendall(message.encode())
            print("Sent:", message)
            time.sleep(5)
        except socket.error:
            print("Failed to send message")
            break

def manage_connection():
    while True:
        if check_connection():
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(('192.168.1.1', 12345))
                print("Connected to server")
                threading.Thread(target=receive_messages, args=(client_socket,)).start()
                send_messages(client_socket)
            except socket.error as e:
                print("Connection failed:", e)
                if client_socket:
                    client_socket.close()
                time.sleep(5)
        else:
            print("Ethernet Disconnected")
            time.sleep(1)

if __name__ == "__main__":
    manage_connection()
