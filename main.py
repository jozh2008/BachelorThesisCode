import requests
import re
from galaxyxml_creator import *
from pprint import pprint
import sys


class Initialize:

    def get_collections(self, url):
        """
            Define the path to the specific endpoint you want to access
        """

        # Make a GET request to retrieve information about available collections
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract the JSON data from the response
            data = response.json()

            return data
        else:
            print("Failed to retrieve collections. Status code:", response.status_code)
            return None


    def json_to_galaxyxml(self, json_data):
        """
        Generate based on the received json file, the corrensponding galaxy xml file and 
        """
        name_id = self.rename_tool(tool_name=json_data["id"])
        name = json_data["id"]
        gxt = Galaxyxmltool(name=name, id=name_id, version=json_data["version"], description=json_data["title"])
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
        #tool.outputs = gxt.define_output_collections()

        tool.executable = gxt.define_command(json_data["id"])
        tool.tests = gxt.define_tests()
        tool.citations = gxt.create_citations()

        file_path = f"Tools/{name}.xml"
        with open(file_path, "w") as file:
            file.write(tool.export())


    def rename_tool(self, tool_name):
        # Replace non-alphanumeric characters with underscores
        cleaned_name = re.sub(r'[^a-zA-Z0-9_-]', '_', tool_name)
        # Convert to lowercase
        cleaned_name = cleaned_name.lower()
        return cleaned_name


def main(base_url, process):
    """
    Define the base URL of the OGC API
    """

    url = f"{base_url}{process}"
    pprint(url)

    # Get collections information
    workflow = Initialize()
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
