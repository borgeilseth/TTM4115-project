import requests

URL = "http://192.168.95.158:5001"


def get_data():
    r = requests.get(url = URL)
    get_data = r.json()
    print(get_data)

