# importing the requests library
import requests
import json

# defining the api-endpoint
API_ENDPOINT = "http://192.168.95.158:5001"



# sending post request and saving response as response object
def post_data(data):
    r = requests.post(url=API_ENDPOINT, json=data)
    print(r.text) # print the response

