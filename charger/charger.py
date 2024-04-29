from stmpy import Machine, Driver
import random
import time
from config import *
import json
import socket

global current_charge

class Charger:
    
    """
        possible states:
            idle
            validating
            charging
            done_charging
            
        possible events:
            connect: idle -> validating
            ok: validating -> charging
            error: validating -> idle
            done_charging: charging -> done_charging
            disconnect: done_charging -> idle
            
        incoming messages:
            connect
            charging
        
        outgoing messages:
            charging
            disconnect
            
    """
    
    def check_user(self):
        "Check user"
        return True

    def check_user_transition(self):
        if Charger.check_user(self):
            self.stm.send("valid_user")
        else:
            self.stm.send("invalid_user")
            
    def check_settings(self):
        print ('checking settings')

    def invalid_error(self):
        print ('not valid user')
    
    def stop_charging(self):
        print ('charging done')

    def on_idle(self):              
        print('Idling')        
        
    def build_message(self) -> dict:
        if self.stm.state() == "charging":
            return {
                "status": "charging",
                "charging_speed": self.charge_speed
            }
        
        if self.stm.state() == "disconnect":
            return {
                "status": "disconnect"
            }
    
    def receive_message(self, message: dict):
        print("Received from car: \n \t", message)


# Transitions
t0 = {
    'trigger': '',
    'source': 'initial',
    'target': 'idle',
    'effect': 'on_idle; start_timer("t", 1000)'
}

#validate
t1 = {
    'trigger': 'connect',
    'source': 'idle',
    'target': 'validating',
    'effect': 'check_user_transition'
}

#start charging
t2 = {
    'trigger': 'valid_user',
    'source': 'validating',
    'target': 'charging',
    'effect': 'check_settings; charge'
}

#error
t3 = {
    'trigger': 'invalid_user',
    'source': 'validating',
    'target': 'idle',
    'effect': 'invalid_error'
}

#done charging
t4 = {
    'trigger': 'done_charging',
    'source': 'charging',
    'target': 'idle',
    'effect': 'stop_charging'
}

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
                

# State machine for the charger
charger = Charger()

machine = Machine(name='charger', transitions=[t0, t1, t2, t3, t4], obj=charger)
charger.stm = machine

driver = Driver()
driver.add_machine(machine)
driver.start()


if __name__ == "__main__":
    start_server()