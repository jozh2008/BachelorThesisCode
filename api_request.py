import requests
from PIL import Image
from io import BytesIO


class APIRequest:
    def __init__(self, url, payload, response_input, output_type, working_directory):
        self.url = url
        self.headers = {
            'accept': '*/*',
            'Prefer': 'return=representation',
            'Content-Type': 'application/json'
        }
        
        self.payload = payload
        self.response_input = response_input
        self.output_type = output_type
        self.working_directory = working_directory

    # Improve for non raw
    def post_request(self):
        response = requests.post(self.url, headers=self.headers, json=self.payload)
        output_data_type = self.normalize_output_type()
        #print(output_data_type)
        if response.ok:
            if self.response_input == "raw":
                included = {"jpeg", "png"}
                if output_data_type[0] in included:
                    # Process image data
                    image_data = BytesIO(response.content)
                    img = Image.open(image_data)
                    img = img.convert('RGB')
                    output_file_path = self.working_directory["output_data"]
                    img.save(output_file_path, format=output_data_type[0].upper())
                else:
                    # Save raw data to file
                    output_file_path = self.working_directory["output_data"]
                    with open(output_file_path, 'wb') as f:
                        f.write(response.content)

            else:
                print(response.json())
                return response.json()
        else:
            print("Error:", response.status_code)
    
    def normalize_output_type(self):
        return list(data_type.split('/')[-1] for data_type in self.output_type)
