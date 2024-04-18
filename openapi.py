#!/usr/bin/env python3
#print("This is a placeholder function.")

import sys
import re
from pprint import pprint

class Api:
    def __init__(self, server, api_key) -> None:
        self.server = server
        self.api_key = api_key


    def print_inputs(self):
        print("This is a placeholder function.")
        # Get command-line arguments
        args = sys.argv[1:]  # Exclude the first argument which is the script name
        attributes = self.convert(args=args)
        print(attributes)
        # Access attributes
        il = attributes.get('il')
        out = attributes.get('out')
        ram = attributes.get('ram')
        exp = attributes.get('exp')
        response = attributes.get("response")
        output_type_1 = attributes.get('outputType1_out')
        self.open_and_read_file(il)

        # Use attributes as needed
        print("Input IL:", il)
        print("Output:", out)
        print("RAM:", ram)
        print("Experiment:", exp)
        print("Output Type 1:", output_type_1)
        print("reponse", response)
    
    def generate_output_list(self, attributes):
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
        
        # Print the list for debugging
        pprint(lst)
        
        # Return the list
        return lst
    
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
                print(file_content)
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

        Example:
        >>> converter = Converter()
        >>> arguments = ['key1', 'value1', 'key2', 'value2']
        >>> converter.convert(arguments)
        {'key1': 'value1', 'key2': 'value2'}
        """
        if len(args) % 2 != 0:
            raise ValueError("The number of arguments must be even.")

        it = iter(args)
        res_dict = dict(zip(it, it))
        return res_dict
    

    def output_json(self,outputName, mediaType, transmissionMode):
        output_format = {
                outputName: {
                    "format": {
                        "mediaType": mediaType
                    },
                    "transmissionMode": transmissionMode
                }
        }
        return output_format
    
    def response_json(self, response):
        output_format = {
            "response": response
        }
        return output_format

    


if __name__ == "__main__":
    api = Api(server="http://127.0.0.1:9090/", api_key="")
    api.print_inputs()
