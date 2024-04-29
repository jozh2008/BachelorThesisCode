#!/home/josh/Documents/GitHub/BachelorThesisCode/.venv/bin/python3
# Run with python3 openapi.py name OTB.BandMath il test_datasets.txt out
# float ram 128 exp 'im1b3,im1b2,im1b1' response raw outputType1_out image/png transmissionMode_1 reference
import sys
import re
from pprint import pprint
from api_request import *


class ApiJson:
    def __init__(self) -> None:
        self.isArray = "isArray"
        self.isexcluededList = []
        self.output_type = []
        self.working_directory = {}
        self.url = "https://ospd.geolabs.fr:8300/ogc-api/processes/"

    def get_json_inputs(self):
        print("This is a placeholder function.")
        # Get command-line arguments
        args = sys.argv[1:]  # Exclude the first argument which is the script name
        attributes = self.convert(args=args)
        pprint(attributes)
        inputs = self.process_input_values(attributes=attributes)
        #pprint(inputs)
        outputs = self.process_output_values(attributes=attributes)
        response = self.process_response_values(attributes=attributes)
        input_json = self.create_openapi_input_file(inputs=inputs, outputs=outputs, response=response)
        pprint(input_json)
        #pprint(self.working_directory)
        apirequest = APIRequest(url=self.get_url(attributes=attributes), payload=input_json, response_input=response, output_type =self.output_type, working_directory = self.working_directory)
        apirequest.post_request()
    
    def modify_attributes(self, attributes):
        """
        Modify attributes by normalizing tool names.

        Args:
            attributes (dict): A dictionary containing attributes to be modified.

        Returns:
            dict: A modified dictionary with normalized tool names.
        """
        return {
            key: self.normalize_tool_name(value) if key != "name" else value
            for key, value in attributes.items()
        }

    def get_url(self, attributes):
        base_url = self.url
        endpoint = attributes["name"]
        return base_url + endpoint + "/execution"

    def process_output_values(self, attributes):
        dictionary_list = self.generate_output_list(attributes=attributes)

        res = self.combine_dicts(dict_list=dictionary_list)
        return res

    def process_response_values(self, attributes):
        response = self.extract_response_value(dictionary=attributes)

        return response
    
    def normalize_tool_name(self, tool_name: str):
        # Replace non-alphanumeric characters with underscores
        cleaned_name = tool_name.replace("_", " ")
        # Convert to lowercase
        return cleaned_name

    def create_openapi_input_file(self, inputs, outputs, response):
        """
        Create an OpenAPI input file.

        Args:
            inputs (dict): A dictionary containing input data.
            outputs (dict): A dictionary containing output data.
            response (str): The response type.

        Returns:
            dict: A dictionary containing inputs, outputs, and response.

        """
        result_dictionary = {}
        result_dictionary["inputs"] = inputs
        result_dictionary["outputs"] = outputs
        result_dictionary["response"] = response
        return result_dictionary

    def process_input_values(self, attributes):
        """
        Process input attributes.

        Extracts input values from the provided attributes dictionary and categorizes them into two types: 
        data inputs, such as text files, and non-data inputs.

        Args:
            attributes (dict): A dictionary containing input attributes.

        Returns:
            dict: A dictionary containing JSON representations of input files.
        """
        # Extract all input values
        all_input_values = self.extract_input_values(attributes)

        # Separate input values with data files
        input_values_with_files = self.extract_data_files(all_input_values)

        # Process input files
        processed_input_files = self.process_files(input_values_with_files, all_input_values)

        # Separate input values without data files
        input_values_without_files = self.extract_non_data_inputs(
            data_inputs=input_values_with_files,
            all_input_values=all_input_values
        )
        modified_non_data_inputs = self.modify_attributes(input_values_without_files)

        # Create input JSON
        input_json = self.create_input_json(
            non_data_inputs=modified_non_data_inputs,
            input_files=processed_input_files
        )

        return input_json

    def process_files(self, input_files, input_schema):
        """
        Process input files by opening and reading them, and add is_array to the list of arrays.
        This is done to later remove it from the input attributes for server compatibility.
        Then generate JSON representations of the files.

        Args:
            input_files (dict): Dictionary containing input file attributes.
            input_schema (dict): Dictionary containing schema information for input files.

        Returns:
            list: List of input file JSON representations.
        """
        input_file_json_list = []
        
        for key, value in input_files.items():
            if "output_data" not in key:
                file_contents = self.open_and_read_file(value)
                exclueded = self.isArray + key
                self.isexcluededList.append(exclueded)
            
                # Determine if the input is an array based on the schema
                if input_schema.get(exclueded) == "False":
                    input_file_json_list.append(self.generate_input_file_json(input_name=key, input_list=file_contents))
                else:
                    input_file_json_list.append(self.generate_input_file_list_json(input_name=key, input_list=file_contents))
            else:
                self.isexcluededList.append(key)
                self.working_directory[key] = value

        return input_file_json_list


    def extract_non_data_inputs(self, data_inputs, all_input_values):
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
        print(self.isexcluededList)
        excluded_prefixes = set(data_inputs.keys()).union(set(self.isexcluededList))
        extracted_values = {
            key: value
            for key, value in all_input_values.items()
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
        keys_transmissionMode = list(transmissionMode.keys())
        values_transmissionMode = list(transmissionMode.values())

        # Initialize an empty list
        lst = []

        # Iterate through the outputs and create dictionaries
        for key, value in zip(keys_transmissionMode, values_transmissionMode):
            output_value = outputs.get(key)
            if output_value is not None:
                self.output_type.append(output_value)
            lst.append(self.output_json(key, output_value, value))

        # Return the list
        return lst


    def extract_data_files(self, dictionary):
        """
        Extract data files from the provided dictionary.

        Args:
            dictionary (dict): A dictionary containing input values.

        Returns:
            dict: A dictionary containing only the key-value pairs representing data files.
        """
        included_prefixes = {".dat", ".txt"}
        return {key: values for key, values in dictionary.items() if any(prefix in values for prefix in included_prefixes)}

    def extract_input_values(self, dictionary):
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
                index = self.find_index_of_character(key, "_")
                modified_key = key[index + 1:]
                extracted_values[modified_key] = value
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
        """
        Create the actual output format for outputs
        """
        output_format = {
            outputName: {
                "transmissionMode": transmissionMode
            }
        }

        if mediaType is not None:
            output_format[outputName]["format"] = {
                "mediaType": mediaType
            }

        return output_format

    def generate_input_file_list_json(self, input_name, input_list):
        """
        Generate JSON representation of a list of input files.

        Args:
            input_name (str): Name of the input.
            input_list (list): List of input file links.

        Returns:
            dict: JSON representation of the input file list.
        """
        input_format = {input_name: [{"href": link} for link in input_list]}
        return input_format

    
    def generate_input_file_json(self, input_name, input_list):
        """
        Generate JSON representation of a single input file.

        Args:
            input_name (str): Name of the input.
            input_list (list): List of input file links.

        Returns:
            dict: JSON representation of the input file.
        """
        input_format = {input_name: {"href": link} for link in input_list}
        return input_format


    def create_input_json(self, non_data_inputs, input_files):
        """
        Create JSON representation of input data.

        Combines non-data inputs and input files into a single dictionary representing the input JSON.

        Args:
            non_data_inputs (dict): A dictionary containing non-data input attributes.
            input_files (dict): A dictionary containing input file attributes.

        Returns:
            dict: A dictionary representing the input JSON.
        """
        # Combine dictionaries in input_files
        combined_dict = self.combine_dicts(input_files)

        # Merge combined_dict with non_data_inputs
        result = self.merge_dicts(non_data_inputs, combined_dict)
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
