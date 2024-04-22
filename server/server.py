from config import *

price_history = []
user_database = {}

def authenticate_client(client_socket):
    password = client_socket.recv(1024)
    if password == b'1234':
        return True
    else:
        return False

def main():
    pass


if __name__ == '__main__':
    main()