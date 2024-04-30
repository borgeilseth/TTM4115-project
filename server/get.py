import requests

URL = "http://192.168.95.194:5001"


r = requests.get(url = URL)

get_data = r.json()

print(get_data)

# post_data = {'ID: 1'}

# q = requests.post(url="http://192.168.95.109:5000", data=post_data)
