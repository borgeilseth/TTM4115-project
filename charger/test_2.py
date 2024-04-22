import socket
import psutil
import time
import threading

def check_connection():
    return "eth0" in psutil.net_if_stats() and psutil.net_if_stats()['eth0'].isup

def handle_client(connection):
    try:
        while True:
            data = connection.recv(1024)
            if not data:
                raise ConnectionResetError
            print("Received from client:", data.decode())
            time.sleep(1)  # Simulate doing some work
    except (ConnectionResetError, socket.timeout):
        print("Client disconnected or timeout")
        connection.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('192.168.1.1', 12345))
    server_socket.listen(1)
    print("Server listening on 192.168.1.1:12345")

    while True:
        if check_connection():
            print("Waiting for a client...")
            connection, addr = server_socket.accept()
            connection.settimeout(10)
            print(f"Connected to {addr}")
            threading.Thread(target=handle_client, args=(connection,)).start()
        else:
            print("Ethernet Disconnected")
        time.sleep(1)
        
server_socket = None
connection = None

def send_messages():
    while True:
        if connection:
            try:
                message = "Server message at {}".format(time.ctime())
                connection.sendall(message.encode())
                print("Sent:", message)
            except socket.error:
                print("Failed to send message")
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=start_server).start()
    send_messages()
