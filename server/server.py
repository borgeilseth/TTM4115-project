from config import *
from ..car.car import set_charge_true, set_charge_false, charge_level, increase_charge
import charger

price_history = []
user_database = {} #database with the users and their passwords
get_user_preference = {} # Assuming get_user_preference() is a function that retrieves the user's preference
price_now = 150 #øre per kWh
grid_level = 50 # % of the grid's capacity used

def add_user(username, password, charge_speed, max_price, charge_limit, mail, car, payment_info):
    user_database[username] = {'password': password, 'charge_speed': charge_speed, 'max_price': max_price, 'charge_limit': charge_limit, 'mail' : mail, 'type_of_car' : car, 'payment_info' : payment_info}

def remove_user(username):
    del user_database[username]

def authenticate_client(username, password):
    if username in user_database and user_database[username] == password:
        return True
    else:
        return False

def server_feature_1(): #feature 1
    print("Accessing feature 1...")

def server_feature_2(): #feature 2
    print("Accessing feature 2...")

def change_charge_speed(user, new_speed):
    user['charge_speed'] = new_speed

def change_max_price(user, new_price):
    user['max_price'] = new_price

def change_charge_limit(user, new_limit):
    user['charge_limit'] = new_limit

def start_charging(user):
    if user.get('max_price') < price_now:
        print("Charging not started. Price too high.")
        set_charge_false()
    if user.get('charge_limit') < charge_level:
        print("Charging not started. Charge limit too low.")
        set_charge_false()
    if grid_level > 90:
        print("Charging not started. Grid level too high.")
        set_charge_false()
    else:
        set_charge_true()
        increase_charge(user.get('charge_limit'), user.get('charge_speed'))  


def main():
    username = input("Enter username: ")
    password = input("Enter password: ")
    add_user(username, password)

    if authenticate_client(username, password):
        print("Access granted.")
        server_feature_1()
        server_feature_2()
        max_price = 100 # This is just an example
        try:
            charger.start_charging(max_price) # Pass max_price to the function in charger.py
        except Exception as e:
            print(f"An error occurred while starting charging: {e}")
    else:
        print("Access denied.")


if __name__ == '__main__':
    main() 
    charger.feature_from_charger() # Call a function from charger.py
