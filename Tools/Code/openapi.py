#!/home/josh/Documents/GitHub/BachelorThesisCode/.venv/bin/python3
# Run with python3 openapi.py name OTB.BandMath il test_datasets.txt out
# float ram 128 exp 'im1b3,im1b2,im1b1' response raw outputType1_out image/png transmissionMode_1 reference
import sys
import re
from pprint import pprint
from api_request import APIRequest
from typing import Dict, List


class ApiJson:
    def __init__(self) -> None:
        self.isArray = "isArray"
        self.exclusion_list = []
        self.output_format_dictionary = {}
        self.file_directory = {}
        self.transmission_mode = {}
        self.prefer = ""

    def get_json_inputs(self):
        print("This is a placeholder function.")
        # Get command-line arguments
        args = sys.argv[1:]  # Exclude the first argument which is the script name
        attributes = self.convert(args=args)
        pprint(attributes)

        prefer = attributes["prefer"]

        inputs = self.process_input_values(attributes=attributes)
        outputs = self.process_output_values(attributes=attributes)
        response = self.process_response_values(attributes=attributes)

        input_json = self.create_openapi_input_file(
            inputs=inputs, outputs=outputs, response="document"
        )
        pprint(input_json)
        apirequest = APIRequest(
            execute=self.get_process_execution(attributes=attributes),
            payload=input_json,
            response_input=response,
            output_format_dictionary=self.output_format_dictionary,
            file_directory=self.file_directory,
            transmission_mode=self.transmission_mode,
            prefer=prefer,
        )
        apirequest.post_request()

    def modify_attributes(self, attributes: Dict):
        """
        Modify attributes by normalizing tool names.

        Args:
            attributes (dict): A dictionary containing attributes to be modified.

        Returns:
            dict: A modified dictionary with normalized tool names.
        """
        return {
            key: self.format_tool_name(value) if key != "name" else value
            for key, value in attributes.items()
        }

    def get_process_execution(self, attributes: Dict):
        """
        Constructs the endpoint URL for the execution of a specific process.

        This method takes a dictionary of attributes, extracts the 'name' attribute,
        and constructs a URL string for the execution of the specified process.

        Args:
            attributes (Dict): A dictionary containing the 'name' attribute
                               which specifies the process endpoint.

        Returns:
            str: A string representing the URL for the process execution endpoint.
        """
        endpoint = attributes["name"]
        return f"processes/{endpoint}/execution"

    def process_output_values(self, attributes: Dict):
        """
        Processes the output values by generating a list of dictionaries based on the given attributes and then
        combining these dictionaries into a single dictionary.

        Parameters:
        attributes (Dict): A dictionary of attributes used to generate the output list.

        Returns:
        Dict: A single combined dictionary resulting from the list of generated dictionaries.
        """
        dictionary_list = self.generate_output_list(attributes=attributes)

        res = self.combine_dicts(dict_list=dictionary_list)
        return res

    def process_response_values(self, attributes):
        """
        Processes and extracts the response value from the provided attributes.

        This method calls extract_response_value to retrieve the value associated
        with a key containing 'response' from the attributes dictionary.

        Args:
            attributes (Dict[str, str]): A dictionary containing various attributes.

        Returns:
            str: The extracted response value, or an empty string if no such key is found.
        """
        response = self.extract_response_value(dictionary=attributes)

        return response

    def format_tool_name(self, tool_name: str) -> str:
        """
        Normalizes a tool name by replacing underscores with spaces and converting it to lowercase.

        This method takes a tool name string, replaces all underscores with spaces,
        and then converts the entire string to lowercase.

        Args:
            tool_name (str): The original tool name string.

        Returns:
            str: The normalized tool name with spaces instead of underscores and in lowercase.
        """
        # Replace underscores with spaces
        cleaned_name = tool_name.replace("_", " ")
        # Convert to lowercase
        return cleaned_name.lower()

    def create_openapi_input_file(
        self, inputs: Dict, outputs: Dict, response: str
    ) -> Dict:
        """
        Creates a dictionary representing an OpenAPI input file.

        This method takes dictionaries for inputs, outputs, and response, and combines them
        into a single dictionary suitable for use as an OpenAPI input file.

        Args:
            inputs (Dict): A dictionary containing input data.
            outputs (Dict): A dictionary containing output data.
            response (str): Containing the response type which is always "document".

        Returns:
            Dict: A dictionary containing the combined inputs, outputs, and response.
        """
        result_dictionary = {}
        result_dictionary["inputs"] = inputs
        result_dictionary["outputs"] = outputs
        result_dictionary["response"] = response
        return result_dictionary

    def process_input_values(self, attributes: Dict):
        """
        Process input attributes.

        This method processes the provided attributes dictionary by extracting and categorizing input values
        into data inputs (such as text files) and non-data inputs. It then processes these inputs and generates
        a JSON representation of the input files.

        Args:
            attributes (Dict): A dictionary containing input attributes.

        Returns:
            Dict: A dictionary containing JSON representations of input files.
        """
        # Extract all input values
        all_input_values = self.extract_input_values(attributes)

        # Separate input values with data files
        input_values_with_files = self.extract_data_files(all_input_values)

        # Process input files
        processed_input_files = self.process_and_generate_input_files(
            input_values_with_files, all_input_values
        )

        # Separate input values without data files
        input_values_without_files = self.extract_non_data_inputs(
            data_inputs=input_values_with_files, all_input_values=all_input_values
        )
        modified_non_data_inputs = self.modify_attributes(input_values_without_files)

        # Create input JSON
        input_json = self.create_input_json(
            non_data_inputs=modified_non_data_inputs, input_files=processed_input_files
        )
        return input_json

    def process_and_generate_input_files(
        self, input_files: Dict[str, str], input_schema: Dict[str, str]
    ) -> List[Dict]:
        """
        Process input files by opening and reading them, and mark arrays for exclusion. A file is an input file
        if it doesn't have the prefix "output_data". If it has "output_data", we mark it for exclusion and
        store its path in the file directory because it contains the file path for the galaxy history.
        Then generate JSON representations of the files.

        Args:
            input_files (Dict[str, str]): Dictionary containing files with their paths.
            input_schema (Dict[str, str]): Dictionary containing schema information for all input values.

        Returns:
            List[Dict]: List of input file JSON representations.
        """
        input_file_json_list = []
        for key, file_path in input_files.items():
            if "output_data" not in key:
                # Adjust key for Cheetah compatibility
                adjusted_key = key.replace("_", ".")  # change back because of Cheetah
                file_contents = self.open_and_read_file(file_path)
                exclusion_key = self.isArray + adjusted_key
                self.exclusion_list.append(exclusion_key)

                # Determine if the input is an array based on the input schema
                if input_schema.get(exclusion_key) == "False":
                    input_file_json_list.append(
                        self.generate_input_file_json(
                            input_name=adjusted_key, input_list=file_contents
                        )
                    )
                else:
                    input_file_json_list.append(
                        self.generate_input_file_list_json(
                            input_name=adjusted_key, input_list=file_contents
                        )
                    )
            else:
                output_key = self.extract_suffix_after_prefix(key).replace("_", ".")
                final_key = f"output_data_{output_key}"
                self.exclusion_list.append(final_key)
                self.file_directory[final_key] = file_path
        # pprint(input_file_json_list)
        return input_file_json_list

    def extract_suffix_after_prefix(self, key: str, prefix: str = "output_data") -> str:
        """
        Extracts the portion of the key following the specified prefix.

        This method takes a key string and a prefix, identifies the substring that starts after the
        specified prefix, and returns this substring. If the prefix is not found, it returns an empty string.

        Args:
            key (str): The original key string that contains the prefix.
            prefix (str): The prefix to search for in the key. Default is 'output_data'.

        Returns:
            str: The substring of the key that follows the prefix. Returns an empty string if the prefix is not found.
        """
        match = re.match(f"{prefix}", key)
        if match:
            index = match.end()
            return key[index + 1 :]
        return ""

    def extract_non_data_inputs(
        self, data_inputs: Dict, all_input_values: Dict
    ) -> Dict:
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
        excluded_prefixes = set(data_inputs.keys()).union(set(self.exclusion_list))
        extracted_values = {
            key: value
            for key, value in all_input_values.items()
            if not any(key.startswith(prefix) for prefix in excluded_prefixes)
        }
        return extracted_values

    def generate_output_list(self, attributes: Dict):
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
        # pprint(outputs)
        transmission_mode = self.extract_transmission_mode_values(attributes)
        # pprint(transmission_mode)
        self.transmission_mode = transmission_mode

        lst = []

        # Iterate through the outputs and create dictionaries
        # for key, value in zip(keys_transmission_mode, values_transmission_mode):
        for key, value in transmission_mode.items():
            output_value = outputs.get(key)

            # We want to return a image, when we have a raw data and value, but we cannot
            # download an image with value, cause no url is given, Therefore we always set the value
            # to reference
            if output_value is not None:
                self.output_format_dictionary[key] = output_value
                if "image" in output_value:
                    value = "reference"

            lst.append(
                self.output_json(
                    outputName=key, mediaType=output_value, transmissionMode=value
                )
            )

        # Return the list

        # pprint(lst)

        return lst

    def extract_data_files(self, dictionary: Dict):
        """
        Extract data files from the provided dictionary.

        Args:
            dictionary (dict): A dictionary containing input values.

        Returns:
            dict: A dictionary containing only the key-value pairs representing data files.
        """
        included_suffixes = {".dat", ".txt"}
        return {
            key: values
            for key, values in dictionary.items()
            if any(values.endswith(suffix) for suffix in included_suffixes)
        }

    def extract_input_values(self, dictionary: Dict):
        """
        Extract input values from a dictionary, excluding certain keys and setting 'prefer'.

        This method filters out keys from the provided dictionary that start with any of the specified
        excluded prefixes. Additionally, it sets the 'prefer' attribute of the object to the value
        associated with the 'prefer' key in the dictionary.

        Args:
            dictionary (dict): The dictionary from which to extract values.

        Returns:
            dict: A new dictionary containing only input values.
        """

        excluded_prefixes = {
            "response",
            "outputType",
            "transmissionMode",
            "name",
            "prefer",
        }
        return {
            key: value  # check if correct
            for key, value in dictionary.items()
            if not any(key.startswith(prefix) for prefix in excluded_prefixes)
        }

    def extract_values_by_keyword(self, dictionary: Dict, keyword: str):
        """
        Extracts values from the input dictionary based on keys containing the given keyword.

        Args:
            dictionary (dict): The dictionary containing key-value pairs.
            keyword (str): The keyword to search for in the keys.

        Returns:
            dict: A new dictionary containing extracted values with modified keys.
        """
        extracted_values = {}
        for key, value in dictionary.items():
            if keyword in key:
                index = self.find_index_of_character(key, "_")
                modified_key = key[index + 1 :].replace("_", ".")  # check if correct
                extracted_values[modified_key] = value
        return extracted_values

    def extract_output_values(self, dictionary: Dict):
        """
        Extracts values from the input dictionary based on keys containing 'outputType'.

        Args:
            dictionary (dict): The dictionary containing key-value pairs.

        Returns:
            dict: A new dictionary containing extracted values with modified keys.
        """
        return self.extract_values_by_keyword(dictionary, "outputType")

    def extract_transmission_mode_values(self, dictionary: Dict):
        """
        Extracts values from the input dictionary based on keys containing 'transmissionMode'.

        Args:
            dictionary (dict): The dictionary containing key-value pairs.

        Returns:
            dict: A new dictionary containing extracted values with modified keys.
        """
        return self.extract_values_by_keyword(dictionary, "transmissionMode")

    def extract_response_value(self, dictionary: Dict):
        """
        Extracts the value associated with a key containing 'response' from a dictionary.

        This method iterates through the provided dictionary, identifies a key that contains
        the substring 'response', and returns the corresponding value. If multiple keys contain
        'response', the value of the last such key is returned. If no such key is found, an
        empty string is returned.

        Args:
            dictionary (Dict[str, str]): A dictionary from which to extract the response value.

        Returns:
            str: The value associated with the key containing 'response', or an empty string if no such key is found.
        """
        extracted_value = ""
        for key, value in dictionary.items():
            if "response" in key:
                extracted_value = value
        return extracted_value

    def find_index_of_character(self, string: str, character: str):
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

    def open_and_read_file(self, file_path: str) -> List[str]:
        """
        Opens and reads the contents of a file.

        This method attempts to open the specified file in read mode, reads its contents line by line,
        and returns a list containing each line of the file as a string.

        Args:
            file_path (str): The path to the file to be opened and read.

        Returns:
            List[str]: A list containing each line of the file as a string.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            Exception: If an error occurs while opening or reading the file.
        """
        try:
            with open(file_path, "r") as file:
                file_content = file.read().splitlines()
                return file_content
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            raise
        except Exception as e:
            print(f"An error occurred while opening the file: {e}")
            raise

    def convert(self, args: List):
        """
        Convert a list of arguments into a dictionary.

        Parameters:
        - args (list): A list of arguments. It should contain an even number of elements,
                    where each pair of elements represents a key-value pair for the resulting dictionary.

        Returns:
        - dict: A dictionary created from the key-value pairs extracted from the input list.

        Raises:
        - ValueError: If the number of elements in the input list is not even, indicating missing values.

        Explanation:
        This function takes a list of arguments and converts them into a dictionary where every two consecutive elements
        in the input list represent a key-value pair in the resulting dictionary.
        """

        if len(args) % 2 != 0:
            raise ValueError("The number of arguments must be even.")

        it = iter(args)
        res_dict = dict(zip(it, it))
        return res_dict

    def output_json(self, outputName: str, mediaType: str, transmissionMode: str):
        """
        Create the JSON representation of an output format.

        This method constructs a dictionary representing the output format, including the output name,
        transmission mode, and optional media type if provided.

        Args:
            outputName (str): The name of the output.
            mediaType (str): The media type of the output format. Can be None.
            transmissionMode (str): The transmission mode of the output.

        Returns:
            dict: A dictionary representing the output format.

        Example:
            >>> output_json("output1", "application/json", "reference")
            {'output1': {'transmissionMode': 'reference', 'format': {'mediaType': 'application/json'}}}
        """
        output_format = {outputName: {"transmissionMode": transmissionMode}}

        if mediaType is not None:
            output_format[outputName]["format"] = {"mediaType": mediaType}

        return output_format

    def generate_input_file_list_json(self, input_name: str, input_list: List):
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

    def generate_input_file_json(self, input_name: str, input_list: List):
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

    def create_input_json(self, non_data_inputs: Dict, input_files: Dict):
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

        This method takes a list of dictionaries and combines them into a single dictionary.
        If there are duplicate keys, the values from later dictionaries in the list overwrite
        the values from earlier dictionaries.

        Args:
            dict_list (List[Dict]): List of dictionaries to combine.

        Returns:
            Dict: Combined dictionary.

        Example:
            >>> combine_dicts([{'a': 1, 'b': 2}, {'b': 3, 'c': 4}])
            {'a': 1, 'b': 3, 'c': 4}
        """

        combined_dict = {}
        for single_dict in dict_list:
            combined_dict.update(single_dict)
        return combined_dict

    def merge_dicts(self, base_dict: dict, overlay_dict: dict) -> dict:
        """
        Merge two dictionaries into a single dictionary.

        This method takes two dictionaries and merges them into a single dictionary.
        If there are duplicate keys, the values from the overlay dictionary (overlay_dict) overwrite
        the values from the base dictionary (base_dict).

        Args:
            base_dict (dict): The base dictionary.
            overlay_dict (dict): The dictionary whose values will overlay the base dictionary.

        Returns:
            dict: The merged dictionary.

        Example:
            >>> merge_dicts({'a': 1, 'b': 2}, {'b': 3, 'c': 4})
            {'a': 1, 'b': 3, 'c': 4}
        """
        merged_dict = base_dict.copy()
        merged_dict.update(overlay_dict)
        return merged_dict

    # def construct_response_json(self, response: str):
    #     """
    #     Create a JSON representation of a response.

    #     This method constructs a dictionary representing the JSON format of a response,
    #     with the response value provided as input.

    #     Args:
    #         response (str): The response value.

    #     Returns:
    #         dict: A dictionary representing the JSON format of the response.
    #     """
    #     output_format = {"response": response}
    #     return output_format


if __name__ == "__main__":
    api = ApiJson()
    api.get_json_inputs()
