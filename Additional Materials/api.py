import requests
import json

base_url = "https://ospd.geolabs.fr:8300/ogc-api/api"
response = requests.get(base_url)
response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

# Extract the JSON data from the response
data = response.json()

with open("api.json", "w") as f:
    json.dump(data,f, indent=4)