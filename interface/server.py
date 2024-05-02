
import requests
import json

# grid_level = 50 # % of the grid's capacity used
API_ENDPOINT = "http://192.168.227.109:5001"


# sending post request and saving response as response object
def post_data(data, URL=API_ENDPOINT) -> dict:
    r = requests.post(URL, json=data)
    return r.text


def get_data(URL=API_ENDPOINT) -> dict:
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
        allow_charging = input("Do you want to allow charging? (y/n)")
        username = input("Enter car to allow charging: ")
        max_charge_percentage = input("Enter max charge percentage: ")
        max_charge_percentage = max_charge_percentage if max_charge_percentage else None
        charging_speed = input("Enter charging speed: ")
        charging_speed = int(charging_speed) if charging_speed else None

        data = {}
        if username:
            old_data_cars = database['allowed_cars']
            old_data_cars.append(username)
            data['allowed_cars'] = old_data_cars
            list_of_allowed_cars = database['allowed_cars']
            if username not in list_of_allowed_cars:
                list_of_allowed_cars.append(username)
                index = list_of_allowed_cars.index(username)
        if allow_charging == 'y':
            data['allow_charging'] = 'True'
        if allow_charging == 'n':
            data['allow_charging'] = 'False'
        if max_charge_percentage is not None:
            data['max_charge_percentage'] = max_charge_percentage
        if charging_speed is not None:
            data['selected_charging_speed'] = charging_speed

        response = post_data(data)
        print(response)
