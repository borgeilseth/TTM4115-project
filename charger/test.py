import socket

def start_client(server_host='10.0.1.1', server_port=65432):
    # Create a socket object using IPv4 and TCP protocol
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to the server
        s.connect((server_host, server_port))
        print("Connected to server.")
        while True:
            # Input message to send to server
            message = input("Enter message to send: ")
            # Send the message to the server
            s.sendall(message.encode())
            # Receive a response from the server
            data = s.recv(1024)
            print("Received from server:", data.decode())

if __name__ == '__main__':
    start_client()
