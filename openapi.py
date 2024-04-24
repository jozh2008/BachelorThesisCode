#!/home/josh/Documents/GitHub/BachelorThesisCode/.venv/bin/python3
# Run with python3 openapi.py name OTB.BandMath il test_datasets.txt out
# float ram 128 exp 'im1b3,im1b2,im1b1' response raw outputType1_out image/png transmissionMode_1 reference
import sys
import re
from pprint import pprint
import json
from api_request import *


class ApiJson:
    def __init__(self) -> None:
        self.isArray = "isArray"
        self.isArrayList = []

    def get_json_inputs(self):
        print("This is a placeholder function.")
        # Get command-line arguments
        args = sys.argv[1:]  # Exclude the first argument which is the script name
        attributes = self.convert(args=args)
        inputs = self.process_input_values(attributes=attributes)
        pprint(inputs)
        outputs = self.process_output_values(attributes=attributes)
        response = self.process_response_values(attributes=attributes)
        input_json = self.create_openapi_input_file(inputs=inputs, outputs=outputs, response=response)
        pprint(input_json)
        apirequest = APIRequest(url=self.get_url(attributes=attributes), payload=input_json, response_input=response)
        apirequest.post_request()

    def get_url(self, attributes):
        base_url = "https://ospd.geolabs.fr:8300/ogc-api/processes/"
        endpoint = attributes["name"]
        return base_url + endpoint + "/execution"

    def process_output_values(self, attributes):
        dictionary_list = self.generate_output_list(attributes=attributes)

        res = self.combine_dicts(dict_list=dictionary_list)
        return res

    def process_response_values(self, attributes):
        response = self.extract_response_value(dictionary=attributes)

        return response

    def create_openapi_input_file(self, inputs, outputs, response):
        result_dictionary = {}
        result_dictionary["inputs"] = inputs
        result_dictionary["outputs"] = outputs
        result_dictionary["response"] = response
        return result_dictionary

    def convert_to_json(self, input_dict):
        return json.dumps(input_dict)

    def process_input_values(self, attributes):
        """
        Process input values and files.

        Extracts all input values from the provided attributes dictionary and then splits them into two categories:
        data inputs, such as text files, and non-data inputs.

        Args:
            attributes: A dictionary containing attributes.

        Returns:
            Dict: A dictionary of input file JSON representations.
        """
        # Extract all input values
        input_values_all = self.extract_input_value(attributes)

        # Separate input values with data files
        input_values_with_input_files = self.get_data_files(dictionary=input_values_all)
        pprint(input_values_with_input_files)

        

        # Process input files
        input_file_json = self.process_input_files(input_values_with_input_files, input_values_all)
        # Separate input values without data files
        input_values_with_non_input_files = self.get_input_non_data(
            attributes_data_input=input_values_with_input_files,
            input_values=input_values_all
        )

        # Create input JSON
        input_json = self.create_input_json(
            input_dictionary=input_values_with_non_input_files,
            input_file_list=input_file_json
        )

        return input_json
    

    def process_input_files(self, input_values_with_input_files, input_schema):
        """
        Process input files. Open data inputs and put it to a list

        Args:
            input_values_with_input_files: Dictionary containing input file attributes.

        Returns:
            List: List of input file JSON representations.
        """
        input_file_json_list = []
        for key, value in input_values_with_input_files.items():
            input_list = self.open_and_read_file(value)
            name = self.isArray+key
            self.isArrayList.append(name)
            if input_schema.get(name) == "False":
                input_file_json_list.append(self.input_file_json_file(inputName=key, input_list=input_list))
            else:
                input_file_json_list.append(self.input_file_list_json_file(inputName=key, input_list=input_list))

        return input_file_json_list

    def get_input_non_data(self, attributes_data_input, input_values):
        """
        Extract non-data input values from the provided input values.

        This method takes a dictionary of input values and a set of prefixes that identify data input keys.
        It returns a dictionary containing only the input values that do not have keys starting with any of the provided prefixes.

        Args:
            attributes_data_input (dict): A dictionary containing keys representing data input prefixes.
            input_values (dict): A dictionary containing all input values.

        Returns:
            dict: A dictionary containing non-data input values.
        """
        print(self.isArrayList)
        excluded_prefixes = set(attributes_data_input.keys()).union(set(self.isArrayList))
        extracted_values = {
            key: value
            for key, value in input_values.items()
            if not any(key.startswith(prefix) for prefix in excluded_prefixes)
        }
        return extracted_values

    def generate_output_list(self, attributes):
        """
        Generate a list of output JSON representations.

        This method extracts output values and transmissionMode values from the provided attributes dictionary,
        converts them to lists, and then iterates through them to create dictionaries representing each output.

        Args:
            attributes (dict): A dictionary containing attributes.

        Returns:
            list: A list of output JSON representations.
        """
        # Extract output values and transmissionMode values
        outputs = self.extract_output_values(attributes)
        transmissionMode = self.extract_transmissionMode_values(attributes)

        # Convert values to lists
        keys_outputs = list(outputs.keys())
        values_outputs = list(outputs.values())
        values_transmisionMode = list(transmissionMode.values())

        # Determine the length of the outputs
        length = len(keys_outputs)

        # Initialize an empty list
        lst = []

        # Iterate through the outputs and create dictionaries
        for i in range(length):
            lst.append(self.output_json(keys_outputs[i], values_outputs[i], values_transmisionMode[i]))

        # Return the list
        return lst

    def get_data_files(self, dictionary):
        """
        Extract data files from the provided dictionary.

        Args:
            dictionary (dict): A dictionary containing input values.

        Returns:
            dict: A dictionary containing only the key-value pairs representing data files.
        """
        included_prefixes = {".dat", ".txt"}
        return {key: values for key, values in dictionary.items() if any(prefix in values for prefix in included_prefixes)}

    def extract_input_value(self, dictionary):
        """
        Extract input values from a dictionary, excluding certain keys.

        Args:
            dictionary (dict): The dictionary from which to extract values.

        Returns:
            dict: A new dictionary containing only input values.
        """

        excluded_prefixes = {"response", "outputType", "transmissionMode", "name"}
        return {
            key: value
            for key, value in dictionary.items()
            if not any(key.startswith(prefix) for prefix in excluded_prefixes)
        }

    def extract_output_values(self, dictionary):
        """
        Extracts values from the input dictionary based on keys containing 'outputType'.

        Args:
            dictionary (dict): The dictionary containing key-value pairs.

        Returns:
            dict: A new dictionary containing extracted values with modified keys.
        """
        extracted_values = {}
        for key, value in dictionary.items():
            if "outputType" in key:
                index = self.find_index_of_character(key, "_")
                modified_key = key[index + 1:]
                extracted_values[modified_key] = value
        return extracted_values

    def extract_transmissionMode_values(self, dictionary):
        extracted_values = {}
        for key, value in dictionary.items():
            if "transmissionMode" in key:
                extracted_values[key] = value
        return extracted_values

    def extract_response_value(self, dictionary):
        extracted_value = ""
        for key, value in dictionary.items():
            if "response" in key:
                extracted_value = value
        return extracted_value

    def find_index_of_character(self, string, character):
        """
        Finds the index of the first occurrence of the specified character in the given string.

        Args:
            string (str): The string to search.
            character (str): The character to search for.

        Returns:
            int: The index of the first occurrence of the character in the string.
        """
        match = re.search(character, string)
        return match.start()

    def open_and_read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                file_content = file.read().splitlines()
                return file_content
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"An error occurred while opening the file: {e}")

    def convert(self, args):
        """
        Convert a list of arguments into a dictionary.

        Parameters:
        - args (list): A list of arguments. It should contain an even number of elements,
                    where each pair of elements represents a key-value pair for the resulting dictionary.

        Returns:
        - dict: A dictionary created from the key-value pairs extracted from the input list.

        Raises:
        - ValueError: If the number of elements in the input list is not even, indicating missing values.

        """
        if len(args) % 2 != 0:
            raise ValueError("The number of arguments must be even.")

        it = iter(args)
        res_dict = dict(zip(it, it))
        return res_dict

    def output_json(self, outputName, mediaType, transmissionMode):
        output_format = {
            outputName: {
                "format": {
                    "mediaType": mediaType
                },
                "transmissionMode": transmissionMode
            }
        }
        return output_format

    def input_file_list_json_file(self, inputName, input_list):
        input_format = {inputName: [{"href": link} for link in input_list]}
        return input_format
    
    def input_file_json_file(self, inputName, input_list):
        input_format = {inputName: {"href": link} for link in input_list}
        return input_format

    def create_input_json(self, input_dictionary, input_file_list):
        # Combine dictionaries in input_file_list
        combined_dict = self.combine_dicts(input_file_list)

        # Merge combined_dict with input_dictionary
        result = self.merge_dicts(input_dictionary, combined_dict)
        return result

    def combine_dicts(self, dict_list):
        """
        Combine dictionaries in a list into a single dictionary.

        Args:
            dict_list (list of dict): List of dictionaries to combine.

        Returns:
            dict: Combined dictionary.
        """
        combined_dict = {}
        for single_dict in dict_list:
            combined_dict.update(single_dict)
        return combined_dict

    def merge_dicts(self, dict1, dict2):
        """
        Merge two dictionaries into a single dictionary.

        Args:
            dict1 (dict): First dictionary.
            dict2 (dict): Second dictionary.

        Returns:
            dict: Merged dictionary.
        """
        merged_dict = dict1.copy()
        merged_dict.update(dict2)
        return merged_dict

    def response_json_format(self, response):
        output_format = {
            "response": response
        }
        return output_format


if __name__ == "__main__":
    api = ApiJson()
    api.get_json_inputs()
