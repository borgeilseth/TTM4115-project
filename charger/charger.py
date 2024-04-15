from config import *
import socket

def main():
host = 'charger.local'
port = 22

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))

server_socket.listen(1)

print("Waiting for conexion...")

client_socket, client_address = server_socket.accept()

print(f"Conexion from: {client_address}")

while True:
    data = client_socket.recv(1024)
    if not data:
        break
    print("The server had recieved:", data.decode())
    
client_socket.close()
server_socket.close()
    pass


if __name__ == '__main__':
    main()
