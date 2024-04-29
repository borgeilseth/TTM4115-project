import socket
import time
import json

class Charger():
    
    charge_speed = 1
    
    def build_message(self) -> dict:
        return {
            "status": "charging",
            "charge_speed": self.charge_speed
        }
    
    def receive_message(self, message: dict):
        print("Received from car: \n \t", message)
        
        
charger = Charger()

def send_message(s, message):
    serialized_message = json.dumps(message)
    s.sendall(serialized_message.encode())

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server started and listening on {host}:{port}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                received_message = json.loads(data.decode())
                charger.receive_message(received_message)
                time.sleep(1)
                response = charger.build_message()
                send_message(conn, response)

if __name__ == "__main__":
    start_server()