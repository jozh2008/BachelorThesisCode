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
        print(output_data_type)
        if response.ok:
            if self.response_input == "raw":

                if output_data_type[0] =="png":
                    image_data = BytesIO(response.content)
        
                    # Open the image
                    img = Image.open(image_data)
                    
                    # Convert the image to 'RGB' mode
                    img = img.convert('RGB')
                    
                    # Specify the output file path
                    output_file_path = self.working_directory["output_data"]
                    
                    # Save the image as PNG format
                    img.save(output_file_path, format='PNG')
                else:
                    image_data = BytesIO(response.content)
                    output_file_path = self.working_directory["output_data"]
                    with open(output_file_path, 'wb') as f:
                        # Write the image data to the file
                        f.write(image_data.getvalue())


            else:
                print(response.json())
                return response.json()
        else:
            print("Error:", response.status_code)
    
    def normalize_output_type(self):
        return list(data_type.split('/')[-1] for data_type in self.output_type)

    def get_request(self):
        response = requests.get(self.url)
        if response.ok:
            print(response)
            print(response.json())
            return response.json()
        else:
            print("Error:", response.status_code)
