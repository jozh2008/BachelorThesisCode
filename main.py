import requests
import re
from galaxyxml_creator import *
from pprint import pprint
import sys


class Initialize:

    def get_collections(self, url):
        """
        Retrieve information about available collections from a specified URL.

        Args:
            url (str): The URL to retrieve the JSON file containing collection information.

        Returns:
            dict or None: A dictionary containing collection information if the request is successful,
                        otherwise None.

        Raises:
            requests.exceptions.RequestException: If an error occurs while making the request.
        """

        try:
            # Make a GET request to retrieve information about available collections
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

            # Extract the JSON data from the response
            data = response.json()
            return data

        except requests.exceptions.RequestException as e:
            print("Failed to retrieve collections:", e)
            return None

    def json_to_galaxyxml(self, json_data):
        """
        Generate a Galaxy XML file based on the received JSON data and store it as an XML file.

        Args:
            json_data (dict): The JSON data representing the tool information.

        """
        name_id = self.rename_tool(tool_name=json_data["id"])
        name = json_data["id"]
        # Create a Galaxy XML tool object
        gxt = Galaxyxmltool(name=name, id=name_id, version=json_data["version"], description=json_data["title"])

        # Generate XML content
        tool = gxt.get_tool()
        tool.requirements = gxt.define_requirements()
        tool.help = (json_data["description"])
        tool.inputs = gxt.create_params(
            input_schema=json_data["inputs"],
            output_schema=json_data["outputs"],
            transmission_schema=json_data["outputTransmission"]
        )

        # two options for tool.outpus need to be discussed
        tool.outputs = gxt.define_output_options()
        # tool.outputs = gxt.define_output_collections()

        tool.executable = gxt.define_command(json_data["id"])
        tool.tests = gxt.define_tests()
        tool.citations = gxt.create_citations()

        file_path = f"Tools/{name}.xml"
        with open(file_path, "w") as file:
            file.write(tool.export())

    def rename_tool(self, tool_name):
        """
        Rename a tool by replacing non-alphanumeric characters with underscores and converting to lowercase.

        Args:
            tool_name (str): The name of the tool to be cleaned.

        Returns:
            str: The cleaned tool name.
        """
        # Replace non-alphanumeric characters with underscores
        cleaned_name = re.sub(r'[^a-zA-Z0-9_-]', '_', tool_name)
        # Convert to lowercase
        cleaned_name = cleaned_name.lower()
        return cleaned_name


def main(base_url, process):
    """
    Main function to process collections data from a base URL and convert it to GalaxyXML.

    Args:
        base_url (str): The base URL.
        process (str): The process to be appended to the base URL.
    """
    url = f"{base_url}{process}"
    pprint(url)

    # Get collections information
    workflow = Initialize()

    # Get collections information
    collections_data = workflow.get_collections(url)

    # Convert JSON to GalaxyXML
    workflow.json_to_galaxyxml(collections_data)


if __name__ == "__main__":
    # Check if the process is provided as a command-line argument
    if len(sys.argv) < 3 or sys.argv[1] != '--process':
        print("Error: API key not provided. Use python3 main.py --process {process}")
        sys.exit(1)
    process = sys.argv[2]
    base_url = "https://ospd.geolabs.fr:8300/ogc-api/processes/"
    main(base_url, process)
