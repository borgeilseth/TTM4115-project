
import requests
import json

# grid_level = 50 # % of the grid's capacity used
API_ENDPOINT = "http://127.0.0.1:5001"


# sending post request and saving response as response object
def post_data(data, URL = API_ENDPOINT) -> dict:
    r = requests.post(URL, json=data)
    return r.json()

def get_data(URL = API_ENDPOINT) -> dict:
    r = requests.get(URL)
    return r.json()




def add_user(username, password, max_charging_percentage, selected_charging_speed): #, charge_speed, charge_limit, mail, car, payment_info):
    user_database = json.loads(get_data())
    if username in user_database:
        print("User already exists.")
        return
    else:
        post_data({'username': username, 'password': password, 'max_charging_percentage': max_charging_percentage, 'selected_charging_speed': selected_charging_speed })
        #user_database[username] = {'password': password}#, 'charge_speed': charge_speed, 'charge_limit': charge_limit, 'mail' : mail, 'type_of_car' : car, 'payment_info' : payment_info}

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
        max_charge_percentage = input("Enter max charge percentage: ")
        charging_speed = input("Enter charging speed: ")
        add_user(username, password, max_charge_percentage, charging_speed)

        if authenticate_client(username, password):
            print("Access granted.")
        else:
            print("Access denied.")
    input("Do you want to see the user database? (y/n)")
    if input == 'y':
        get_data() # Call a function from get.py
    input("Do you want to update the user database? (y/n)")
    if input == 'y':
        username2 = input("Enter username: ")
        password2 = input("Enter password: ")
        max_charge_percentage2 = input("Enter max charge percentage: ")
        charging_speed2 = input("Enter charging speed: ")
        post_data({'username': username, 'password': password, 'max_charging_percentage': max_charge_percentage, 'selected_charging_speed': charging_speed })



if __name__ == '__main__':
    d = get_data()
    print(d)

    d = post_data({
        "allowed_cars": [1, 2, 3],
    })
    print(d)
    
    # main() 
    #charger.feature_from_charger() # Call a function from charger.py


{'Max_charge_percentage': 80, 'Charging_speed': 1, 'Allow_charging': True, 'Allowed_cars': [1]}