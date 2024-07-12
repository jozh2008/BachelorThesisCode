import requests
import re
from GeneratorXML.galaxyxml_creator import GalaxyXmlTool
from pprint import pprint
import sys


class GalaxyToolConverter:

    def retrieve_collections(self, url):
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

    def json_to_galaxyxml(self, process_data, api_data):
        """
        Generate a Galaxy XML file based on the received JSON data and store it as an XML file.

        Args:
            json_data (dict): The JSON data representing the tool information.

        """
        name_id = self.rename_tool(tool_name=process_data["id"])
        name = process_data["id"]
        # Create a Galaxy XML tool object
        gxt = GalaxyXmlTool(
            name=name,
            id=name_id,
            version=process_data["version"],
            description=process_data["title"],
        )

        # Generate XML content
        tool = gxt.get_tool()
        tool.requirements = gxt.define_requirements()
        tool.help = process_data["description"]
        tool.inputs = gxt.create_params(
            input_schema=process_data["inputs"],
            output_schema=process_data["outputs"],
            transmission_schema=process_data["outputTransmission"],
        )

        # two options for tool.outpus need to be discussed
        tool.outputs = gxt.define_output_options()

        tool.executable = gxt.define_command(process_data["id"])
        tool.tests = gxt.define_tests(api_dict=api_data["paths"], process=process_data["id"])
        tool.citations = gxt.create_citations()
        gxt.define_macro()
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
        cleaned_name = re.sub(r"[^a-zA-Z0-9_-]", "_", tool_name)
        # Convert to lowercase
        cleaned_name = cleaned_name.lower()
        return cleaned_name


def main(base_url: str, process_name: str):
    """
    Main function to process collections data from a base URL and convert it to GalaxyXML.

    Args:
        base_url (str): The base URL.
        process (str): The process to be appended to the base URL.
    """
    url = f"{base_url}processes/{process_name}"
    pprint(url)
    url_api = f"{base_url}api"
    print(url_api)
    # Get collections information
    workflow = GalaxyToolConverter()

    # Get collections information
    collections_data = workflow.retrieve_collections(url=url)
    api_data = workflow.retrieve_collections(url=url_api)

    # Convert JSON to GalaxyXML
    workflow.json_to_galaxyxml(process_data=collections_data, api_data=api_data)


if __name__ == "__main__":
    # Check if the process is provided as a command-line argument
    if len(sys.argv) < 3 or sys.argv[1] != "--process":
        print("Error: Process not provided. Use python3 main.py --process {process}")
        sys.exit(1)
    process_name = sys.argv[2]
    BASE_URL = "https://ospd.geolabs.fr:8300/ogc-api/"
    main(BASE_URL, process_name)
