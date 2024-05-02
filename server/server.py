
import requests
import json

# grid_level = 50 # % of the grid's capacity used
API_ENDPOINT = "http://127.0.0.1:5001"


# sending post request and saving response as response object
def post_data(data, URL = API_ENDPOINT) -> dict:
    r = requests.post(URL, json=data)
    return r.text

def get_data(URL = API_ENDPOINT) -> dict:
    r = requests.get(URL)
    return r.json()


def main():
    return

if __name__ == '__main__':
    database = get_data()
    svar = input("Do you want to print the user database? (y/n)")
    if svar == 'y':
        print(database)

    oppdatere = input("Do you want to update the user database? (y/n)")
    if oppdatere == 'y':
        username = input("Enter username: ")
        max_charge_percentage = input("Enter max charge percentage: ")
        max_charge_percentage = max_charge_percentage if max_charge_percentage else None
        charging_speed = input("Enter charging speed: ")
        charging_speed = int(charging_speed) if charging_speed else None

        data = {'allowed_cars': username}
        if max_charge_percentage is not None:
            data['max_charging_percentage'] = max_charge_percentage
        if charging_speed is not None:
            data['selected_charging_speed'] = charging_speed

        response = post_data(data)
        print(response)
    
    
    
