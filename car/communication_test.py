import socket
import json

class Car():
    capacity = 100
    current_charge = 0
    
    def build_message(self) -> str:
        return {
            "status": "charging",
            "current_charge": self.current_charge,
            "capacity": self.capacity
        }
    
    def receive_message(self, message: dict):
        if message["status"] == "charging":
            self.current_charge += message["charge_speed"]
            if self.current_charge > self.capacity:
                self.current_charge = self.capacity
        print("Received from server: \n \t", message)
        

car = Car()

def send_message(s, message):
    serialized_message = json.dumps(message)
    s.sendall(serialized_message.encode())
    
def start_client(server_host='127.0.0.1', server_port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_host, server_port))
        print("Connected to server")
        while True:
            message = car.build_message()
            send_message(s, message)
            data = s.recv(1024)
            if not data:
                break
            received_message = json.loads(data.decode())
            car.receive_message(received_message)

if __name__ == "__main__":
    start_client()
