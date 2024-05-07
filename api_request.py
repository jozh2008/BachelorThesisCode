import requests
from PIL import Image
from PIL import UnidentifiedImageError
from io import BytesIO
from pprint import pprint


class APIRequest:
    def __init__(self, url, payload, response_input, output_format_dictionary, working_directory, transmission_mode):
        self.url = url
        self.headers = {
            'accept': '*/*',
            'Prefer': 'return=representation',
            'Content-Type': 'application/json'
        }
        
        self.payload = payload
        self.response_input = response_input
        self.output_format_dictionary = output_format_dictionary
        self.working_directory = working_directory
        self.transmission_mode = transmission_mode

    # Improve for non raw, and more than one data type
    def post_request(self):
        """
         Makes a POST request and processes the response data according to specified conditions.
        """
        response = requests.post(self.url, headers=self.headers, json=self.payload)
        if response.ok:
            for key, value in self.transmission_mode.items():
                output_format_path = self.output_format_dictionary.get(key)
                if output_format_path is not None:
                    output_format = output_format_path.split('/')[-1]
                else:
                    output_format="txt"
                location = f"output_data_{key}"
                output_file_path = self.working_directory[location]
                
                if self.response_input == "raw":
                    included = {"jpeg", "png"}
                    if output_format in included:
                        
                        # Process image data
                        try:
                            # Open the image file
                            image_data = BytesIO(response.content)
                            img = Image.open(image_data)
                            img = img.convert('RGB')
                            img.save(output_file_path, format=output_format.upper())
                            
                        except UnidentifiedImageError as e:
                            # Handle the exception
                            error_message = "Error: Cannot identify image file"

                            with open(output_file_path, 'wb') as f:
                                f.write(error_message.encode())
                                f.write(b'\n')  # Add a new line
                                f.write(response.content)
                    else:
                        # Save raw data to file
                        with open(output_file_path, 'wb') as f:
                            f.write(response.content)

                else:
                    response_data = response.json()
                    transmission_item = response_data.get(key)
                    if transmission_item is not None:
                        with open(output_file_path, "w") as f:
                            if value == "reference":
                                f.write(transmission_item.get("href", "") + "\n")
                            else:
                                pprint(transmission_item, stream=f)
        else:
            print("Error:", response.status_code)
    

    # an option for the output
    def post_request2(self):
        response = requests.post(self.url, headers=self.headers, json=self.payload)
        if response.ok:
            response_data = response.json()
            for key, value in self.transmission_mode.items():
                transmission_item = response_data.get(key)
                output_file_path = key + ".txt"
                if transmission_item is not None and value == "reference":
                    
                    pprint(transmission_item["href"])
                    with open(output_file_path, "w") as f:
                        f.write((transmission_item["href"]) + "\n")
        else:
            print("Error:", response.status_code)

