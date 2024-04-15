from config import *
import socket

def main():
    host = 'charger.local'  # IP del servidor
    port = 22  # Puerto de comunicación
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    client_socket.connect((host, port))
    client_socket.sendall(b'Send Password') #First the client send the password to conect to the charager
    
    # Send data to the charger
    client_socket.sendall(b'Request to charge')
    
    client_socket.close()
    pass


if __name__ == '__main__':
    main()
