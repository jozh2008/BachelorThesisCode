#!/usr/bin/env python3
#print("This is a placeholder function.")

import sys
# from galaxytools_workflow import GalaxyWorkflow

class Api:
    def __init__(self, server, api_key) -> None:
        self.server = server
        self.api_key = api_key


    def print_inputs(self):
        print("This is a placeholder function.")
        # Get command-line arguments
        args = sys.argv[1:]  # Exclude the first argument which is the script name
        attributes = self.convert(args=args)
        #gi = GalaxyWorkflow(server=self.server, api_key=self.api_key)
        #gi.get_all_histories()
        #gi.get_datasets_in_history()
        # Access attributes
        il = attributes.get('il')
        out = attributes.get('out')
        ram = attributes.get('ram')
        exp = attributes.get('exp')
        output_type_1 = attributes.get('output_type_1')
        self.open_and_read_file(il)

        # Use attributes as needed
        print("Input IL:", il)
        print("Output:", out)
        print("RAM:", ram)
        print("Experiment:", exp)
        print("Output Type 1:", output_type_1)
    
    def open_and_read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                file_content = file.read().splitlines()
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

    def output_json(self, mediaType, transmissionMode):
        output_format = {
            "outputs": {
                "result": {
                    "format": {
                        "mediaType": mediaType
                    },
                    "transmissionMode": transmissionMode
                }
            }
        }
        return output_format

    


if __name__ == "__main__":
    api = Api(server="http://127.0.0.1:9090/", api_key="")
    api.print_inputs()
