import requests
from PIL import Image
from io import BytesIO


class APIRequest:
    def __init__(self, url, payload, response_input):
        self.url = url
        self.headers = {
            'accept': '*/*',
            'Prefer': 'return=representation',
            'Content-Type': 'application/json'
        }
        self.payload = payload
        self.response_input = response_input

    def post_request(self):
        response = requests.post(self.url, headers=self.headers, json=self.payload)
        if response.ok:
            if self.response_input == "raw":
                image_data = BytesIO(response.content)
                img = Image.open(image_data)

                # Convert the image to 'RGB' mode
                img = img.convert('RGB')

                # Save the image as PNG
                img.save("output.png")

            else:
                print(response.json())
                return response.json()
        else:
            print("Error:", response.status_code)

    def get_request(self):
        response = requests.get(self.url)
        if response.ok:
            print(response)
            print(response.json())
            return response.json()
        else:
            print("Error:", response.status_code)
