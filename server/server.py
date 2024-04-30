#from ..car.car import set_charge_true, set_charge_false, increase_charge
#from car import car as car
#import charger.charger as charger
from get import get_data
from post import post_data

user_database = {} #database with the users and their passwords
get_user_preference = {} # Assuming get_user_preference() is a function that retrieves the user's preference
grid_level = 50 # % of the grid's capacity used



def add_user(username, password, charge_speed, max_price, charge_limit, mail, car, payment_info):
    if username in user_database:
        print("User already exists.")
        return
    else:
        user_database[username] = {'password': password, 'charge_speed': charge_speed, 'max_price': max_price, 'charge_limit': charge_limit, 'mail' : mail, 'type_of_car' : car, 'payment_info' : payment_info}

def remove_user(username):
    del user_database[username]

def authenticate_client(username, password):
    if username in user_database and user_database[username] == password:
        return True
    else:
        return False

def change_charge_speed(user, new_speed):
    user['charge_speed'] = new_speed

def change_charge_limit(user, new_limit):
    user['charge_limit'] = new_limit

def start_charging(user):
    if user.get('charge_limit') < 80: #car.charge_level:
        print("Charging not started. Charge limit too low.")
        #car.set_charge_false()
        return False
    if grid_level > 90:
        print("Charging not started. Grid level too high.")
        #car.set_charge_false()
        return False
    else:
        #car.set_charge_true()
        #car.increase_charge(user.get('charge_limit'), user.get('charge_speed'))  
        return True

def main():
    input("Do you want to add a user? (y/n)")
    if input == 'y':
        username = input("Enter username: ")
        password = input("Enter password: ")
        add_user(username, password)

        if authenticate_client(username, password):
            print("Access granted.")
        else:
            print("Access denied.")
    input("Do you want to see the user database? (y/n)")
    if input == 'y':
        get_data() # Call a function from get.py



if __name__ == '__main__':
    main() 
    #charger.feature_from_charger() # Call a function from charger.py
