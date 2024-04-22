import socket
from sense_hat import SenseHat

def start_server(host='10.0.1.1', port=65432):
    sense = SenseHat()
    
    # Create a socket object using IPv4 and TCP protocol
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the host and port
        s.bind((host, port))
        # Listen for incoming connections
        s.listen()
        print("Server started. Waiting for connection...")
        # Accept any incoming connection
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                # Receive data from the client
                data = conn.recv(1024)
                if not data:
                    break
                # Print received message
                print("Received:", data.decode())
                sense.show_message(data.decode())
                # Send a response back to the client
                conn.sendall(data)

if __name__ == '__main__':
    start_server()
