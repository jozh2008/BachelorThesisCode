import requests
from PIL import Image
from PIL import UnidentifiedImageError
from io import BytesIO
from pprint import pprint
import time


class APIRequest:
    def __init__(self, execute, payload, response_input, output_format_dictionary, working_directory, transmission_mode, prefer):
        self.execute = execute
        self.headers = {
            'accept': '*/*',
            'Prefer': prefer,
            'Content-Type': 'application/json'
        }

        self.payload = payload
        self.response_input = response_input
        self.output_format_dictionary = output_format_dictionary
        self.working_directory = working_directory
        self.transmission_mode = transmission_mode
        self.accept_header = {"accept": "application/json"}
        self.base_url = "https://ospd.geolabs.fr:8300/ogc-api/"
        self.jobs = "jobs/"
        self.job_id = ""
        self.results = "/results"

    # Improve for non raw, and more than one data type
    def post_request(self):
        """
        Makes a POST request and processes the response data according to specified conditions.

        Parameters:
            - `self.transmission_mode`: Contains output names as keys and either "reference" or "value" as values,
            representing the selection made in the Galaxy interface.
            - `self.output_format_dictionary`: Maps output names to the format of the corresponding Galaxy dataset
            if the option was available in the Galaxy interface. Not all keys in `self.transmission_mode` may be present.
            - `self.working_directory`: Stores the path for the output Galaxy datasets, where each dataset path
            is stored as a combination of "output_data_" and the corresponding output name.

        Notes:
            If "raw" is chosen in the Galaxy interface, the method writes `response.content` to the corresponding file.
            Otherwise, it determines whether the transmission mode is "reference" or "value" and writes the appropriate
            data accordingly.
        """
        url = self.get_url(keyword="execute")
        response = requests.post(url, headers=self.headers, json=self.payload)
        response = self.check_job_id(response=response)
        if response.ok:
            for key, value in self.transmission_mode.items():
                output_format_path = self.output_format_dictionary.get(key)
                if output_format_path is not None:
                    output_format = output_format_path.split('/')[-1]
                else:
                    output_format = "txt"
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

                        except UnidentifiedImageError:
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

    def check_job_id(self, response):
        """
        Checks if the response status code is 201. If so, it indicates that the job is still running.
        Continuously checks the job status every 20 seconds. If the job fails, returns an error message;
        otherwise, returns the result.

        Parameters:
            - response: The response object obtained from the POST request.

        Returns:
            - The response object containing the job result, if available.

        Note:
            The method waits for the job to complete or fail before returning the response.
        """
        if (response.status_code == 201):
            response_data = response.json()
            status = response_data["status"]
            self.job_id = response_data["jobID"]
            url = self.get_url(keyword="jobs")
            while (status == "running"):
                time.sleep(20)
                response = requests.get(url=url, headers=self.accept_header)
                response_data = response.json()
                status = response_data["status"]
            url = self.get_url(keyword="results")
            response = requests.get(url=url, headers=self.accept_header)
            if status == "failed":
                print(f"An error occurred. For further details, check OGC Job status through "
                      f"https://ospd.geolabs.fr:8300/ogc-api/jobs/{self.job_id}")

        return response

    def get_url(self, keyword):
        """
        Generates the URL based on the provided keyword.

        Parameters:
            - keyword: A string specifying the type of URL required. Accepted values are "execute", "jobs", and "results".

        Returns:
            - The URL corresponding to the provided keyword.
        """
        url_dictionary = {
            "execute": f"{self.base_url}{self.execute}",
            "jobs": f"{self.base_url}{self.jobs}{self.job_id}",
            "results": f"{self.base_url}{self.jobs}{self.job_id}{self.results}"
        }
        return url_dictionary[keyword]

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
            print("Error: ", response.status_code)
