import requests

URL = "http://192.168.95.109:5000"


r = requests.get(url = URL)

data = r.json()

print(data)