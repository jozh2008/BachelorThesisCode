import requests

class APIRequest:
    def __init__(self, url, payload):
        self.url = url
        self.headers = {
            'accept': '*/*',
            'Prefer': 'return=representation',
            'Content-Type': 'application/json'
        }
        self.payload = payload
    
    def post_request(self):
        response = requests.post(self.url, headers=self.headers, json=self.payload)
        if response.ok:
            print(response.json())
            return response.json()
        else:
            print("Error:", response.status_code)
    
    def get_request(self):
        response = requests.get(self.url)
        if response.ok:
            print(response.json())
            return response.json()
        else:
            print("Error:", response.status_code)
