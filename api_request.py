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
            for i, transmissionMode in enumerate(self.transmissionMode, start=1):
                location = f"output_data_{i}"
                output_file_path = self.working_directory[location]
                if self.response_input == "raw":
                    if i <= len(output_data_type):
                        output_type = output_data_type[i-1]
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
                    if transmissionMode=="reference":
                        # To do: How to proceed if the answer is a value? 
                        print((output_data_type))
                        print((list(response.json().values())))
                        if len(output_data_type) ==len(list(response.json().values())):
                            href_list = [list(response.json().values())[i-1]['href']]
                        else:
                            print(response.json().values())
                            href_list = [value['href'] for value in response.json().values()]
                        with open(output_file_path, "w") as f:
                            f.write("\n".join(href_list) + "\n")
                    else:
                        self.write_href_to_file(response=response, index = i, output_data_type=output_data_type, output_file_path=output_file_path)

        else:
            print("Error:", response.status_code)
    
    def write_href_to_file(self, response, index,  output_file_path, output_data_type):
        """
        Write href data from the response to a file.

        Parameters:
            response (Response): The response object containing JSON data.
            output_file_path (str): The file path where the output will be saved.
            output_data_type (list): List containing data types.

        Returns:
            None
        """
        json_data = response.json()

        values_list = list(json_data.values())
        if len(values_list) == len(output_data_type):
            href_dict = values_list[index - 1]  # assuming i is defined elsewhere
        else:
            href_dict = json_data

        with open(output_file_path, "w") as f:
            pprint(href_dict, stream=f)


    
    def normalize_output_type(self):
        return list(data_type.split('/')[-1] for data_type in self.output_type)
