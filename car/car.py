from config import *
import socket
from sense_hat import SenseHat
import time

sense = SenseHat()

charge_level = 0
charging = True

green = (0,255,0)
red = (255,0,0)
pink = (255,0,255)
blue = (0, 191, 255)

def set_charge_level(input_charge):
    global charge_level
    if input_charge > 100 or input_charge < 0:
        return
    else:    
        charge_level = input_charge

def increase_charge():
    global charge_level
    if charge_level < 100:
        charge_level += 1

def decrease_charge():
    global charge_level
    if charge_level > 0:
        charge_level -= 1

while True:
    if charging == True:
        sense.show_message(str(charge_level)+"%", back_colour=green, text_colour=pink)
        time.sleep(1)
        increase_charge()

    else:
        sense.show_message(str(charge_level)+"%", back_colour=red, text_colour=blue)
        time.sleep(3)
        decrease_charge()
    

   
def main():
    host = 'charger.local'
    port = 22
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    client_socket.connect((host, port))
    client_socket.sendall(b'Send Password') #First the client send the password to conect to the charager
    
    # Send data to the charger
    client_socket.sendall(b'Request to charge')
    
    client_socket.close()
    pass
    


if __name__ == '__main__':
    main()
