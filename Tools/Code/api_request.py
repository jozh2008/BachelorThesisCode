import requests
import sys
from typing import Any
from pprint import pprint
import time
import urllib.request


class APIRequest:
    def __init__(
        self,
        execute,
        payload,
        response_input,
        output_format_dictionary,
        file_directory,
        transmission_mode,
        prefer,
    ):
        self.execute = execute
        self.headers = {
            "accept": "*/*",
            "Prefer": prefer,
            "Content-Type": "application/json",
        }

        self.payload = payload
        self.response_input = response_input
        self.output_format_dictionary = output_format_dictionary
        self.file_directory = file_directory
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
        pprint(url)
        response = requests.post(url, headers=self.headers, json=self.payload)
        response = self.check_job_id(response=response)
        if not response.ok:
            self.handle_response_error(response)
            return

        response_data = response.json()
        pprint(response_data)
        self.process_response_data(response_data)

    def handle_response_error(self, response):
        """
        Handles the error based on the HTTP response status code.

        Parameters:
        - response: The HTTP response object containing the status code.

        This function prints an error message to stderr based on the status code.
        It first attempts to get a specific error message using the get_error_message method.
        If no specific error message is found, it prints a generic error message with the status code.
        """
        error_message = self.get_error_message(response.status_code)
        print(error_message, file=sys.stderr)

    def process_response_data(self, response_data):
        """
        Processes response data based on the transmission mode.

        Parameters:
            - response_data (dict): Dictionary containing response data.

        This method iterates over the keys of `transmission_mode`, retrieves the corresponding
        transmission item from `response_data`, determines the output file path, and writes the
        transmission item to the file based on the specified mode.

        Parameters:
            - response_data (dict): Dictionary containing response data.

        Returns:
            None
        """
        for key, value in self.transmission_mode.items():
            transmission_item = response_data.get(key)
            pprint(transmission_item)
            if transmission_item is None:
                continue
            output_file_path = self.get_output_file_path(key)
            self.write_transmission_item_based_on_mode(output_file_path, transmission_item, value)

    def get_output_file_path(self, key):
        """
        Retrieves the output file path based on the provided key.

        Parameters:
            - key (str): Key to identify the output file path.

        Returns:
            - str: Output file path corresponding to the key.
        """
        location = f"output_data_{key}"
        return self.file_directory[location]

    def write_transmission_item_based_on_mode(self, output_file_path, transmission_item, mode):
        """
        Writes the transmission item to the specified output file path based on the mode.

        Parameters:
            - output_file_path (str): Path to the output file.
            - transmission_item (dict or any): Item to be written to the file.
            - mode (str): Mode of transmission, either "reference" or "value".

        If the response_input attribute is set to "raw", calls write_raw_transmission_item with
        the output_file_path and transmission_item. Otherwise, calls write_transmission_item
        with the output_file_path, transmission_item, and mode.
        """
        if self.response_input == "raw":
            self.write_raw_transmission_item(output_file_path, transmission_item)
        else:
            self.write_transmission_item(
                output_file_path=output_file_path,
                transmission_item=transmission_item,
                mode=mode,
            )

    def write_raw_transmission_item(self, output_file_path, transmission_item):
        """
        Writes the transmission item to the specified output file path in raw format.

        Parameters:
            - output_file_path (str): Path to the output file.
            - transmission_item (dict or any): Item to be written to the file.

        If transmission_item is a dictionary, retrieves the URL from the 'href' field and
        downloads the file from that URL to the specified output_file_path using urllib.request.urlretrieve.
        If transmission_item is not a dictionary, assumes it's a reference and calls write_transmission_item
        with output_file_path, transmission_item, and mode="reference".
        """
        if isinstance(transmission_item, dict):
            url_file = transmission_item.get("href")
            if url_file:
                urllib.request.urlretrieve(url_file, output_file_path)
        else:
            self.write_transmission_item(
                output_file_path=output_file_path,
                transmission_item=transmission_item,
                mode="reference",
            )

    def write_transmission_item(self, output_file_path: str, transmission_item: Any, mode: str):
        """
        Writes the transmission item to the specified file.

        Parameters:
            - output_file_path (str): The path to the output file.
            - transmission_item (dict or any): The item to be written to the file.
            - mode (str): The mode of transmission, either "reference" or "value".

        If the mode is "reference", writes the "href" field from the transmission item.
        Otherwise, pretty-prints the transmission item to the file.
        """
        with open(output_file_path, "w") as f:
            if mode == "reference":
                f.write(transmission_item.get("href", "") + "\n")
            else:
                pprint(transmission_item, stream=f)

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
        if response.status_code == 201:
            response_data = response.json()
            status = response_data["status"]
            self.job_id = response_data["jobID"]
            url = self.get_url(keyword="jobs")
            print(url)
            while status == "running":
                print(status)
                time.sleep(20)
                response = requests.get(url=url, headers=self.accept_header)
                response_data = response.json()
                status = response_data["status"]
            print(status)
            url = self.get_url(keyword="results")
            response = requests.get(url=url, headers=self.accept_header)
            if status == "failed":
                print(
                    f"An error occurred. For further details, check OGC Job status through "
                    f"https://ospd.geolabs.fr:8300/ogc-api/jobs/{self.job_id}",
                    file=sys.stderr,
                )
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
            "results": f"{self.base_url}{self.jobs}{self.job_id}{self.results}",
        }
        return url_dictionary[keyword]

    def get_error_message(self, keyword):
        """
        Retrieves an error message based on the provided HTTP status code.

        Parameters:
        - keyword (int): The HTTP status code for which to retrieve the error message.

        Returns:
        - str: The corresponding error message for the given status code. If the status code
               is not found in the predefined dictionary, a default message is returned
               indicating the unknown status code.
        """

        error_dictionary = {
            500: "500 Internal Server Error",
            405: "405 Method Not Allowed",
            404: "404 Not Found",
            400: "400 Bad Request",
        }
        return error_dictionary.get(keyword, f"Error with HTTP response status code: {keyword}")
