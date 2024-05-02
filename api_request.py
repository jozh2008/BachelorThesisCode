import requests
from PIL import Image
from io import BytesIO
from pprint import pprint


class APIRequest:
    def __init__(self, url, payload, response_input, output_type, working_directory, transmissionMode):
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
        self.transmissionMode = transmissionMode

    # Improve for non raw, and more than one data type
    def post_request(self):
        response = requests.post(self.url, headers=self.headers, json=self.payload)
        if response.ok:
            output_data_type = self.normalize_output_type()
            for i, output_type in enumerate(output_data_type, start=1):
                location = f"output_data_{i}"
                output_file_path = self.working_directory[location]
                if self.response_input == "raw":
                    included = {"jpeg", "png"}
                    if output_type in included:
                        # Process image data
                        image_data = BytesIO(response.content)
                        img = Image.open(image_data)
                        img = img.convert('RGB')
                        img.save(output_file_path, format=output_type.upper())
                    else:
                        # Save raw data to file
                        with open(output_file_path, 'wb') as f:
                            f.write(response.content)

                else:
                    if self.transmissionMode[i-1]=="reference":
                        #href_list = [value['href'] for value in (response.json()).values()]
                        href_list = [list(response.json().values())[i-1]['href']]
                        with open(output_file_path, "w") as f:
                            f.write("\n".join(href_list) + "\n")
                    else:
                        # Assuming response.json() returns a dictionary
                        json_data = response.json()

                        # Accessing values from the dictionary and converting to list
                        values_list = list(json_data.values())

                        # Now you can access elements from the list using indexes
                        href_dict = values_list[i-1]

                        # Writing href_list to the output file
                        with open(output_file_path, "w") as f:
                                pprint(href_dict, stream=f)

        else:
            print("Error:", response.status_code)
    
    def normalize_output_type(self):
        return list(data_type.split('/')[-1] for data_type in self.output_type)
