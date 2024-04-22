from config import *
from car import set_charge_true, set_charge_false
import socket

authenticated = True

if authenticated:
    set_charge_true()
else:
    set_charge_false()

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
        if data.strip() == b'Requirenment for conexion': #Our requirenment could be the log-in user or the password
            print("Conexion Permited")
            break
        else:
            print("Conexion Not Permited")
            client_socket.close()

    while True:
        data = client_socket.recv(1024)  # Recibe datos del cliente
        if not data:
            break
            
    print("We had recieved:", data.decode())
        
    client_socket.close()
    server_socket.close()
    pass


if __name__ == '__main__':
    main()
