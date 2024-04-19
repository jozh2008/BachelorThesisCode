import requests
import re
from galaxyxml_creator import *
from pprint import pprint



def get_collections(base_url):
    """Define the path to the specific endpoint you want to access
    """
    endpoint = "/processes/OTB.BandMath"
    #endpoint = "/processes/OTB.HooverCompareSegmentation"   
    # Construct the full URL
    url = base_url + endpoint

    # Make a GET request to retrieve information about available collections
    response = requests.get(url)
    print(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Extract the JSON data from the response
        data = response.json()
        
        return data
    else:
        print("Failed to retrieve collections. Status code:", response.status_code)
        return None
    
def json_to_galaxyxml(json_data):
    name_id = rename_tool(tool_name=json_data["id"])
    gxt = Galaxyxmltool(name=json_data["id"], id=name_id, version=json_data["version"], description=json_data["title"])
    tool = gxt.get_tool()
    #tool.executable = gxt.define_command(json_data["id"])
    tool.requirements = gxt.define_requirements()
    tool.help = (json_data["description"])
    #pprint(tool.export())
    tool.inputs = gxt.create_params(inputs_json=json_data["inputs"], outputs_json = json_data["outputs"], output_transmission_json=json_data["outputTransmission"])
    tool.outputs = gxt.define_output_options()
    #pprint(json_data["inputs"])
    tool.tests = gxt.define_tests()
    tool.citations = gxt.create_citations()
    #pprint(tool.export())
    with open("output.xml", "w") as file:
        file.write(tool.export())
    






def rename_tool(tool_name):
    # Replace non-alphanumeric characters with underscores
    cleaned_name = re.sub(r'[^a-zA-Z0-9_-]', '_', tool_name)
    # Convert to lowercase
    cleaned_name = cleaned_name.lower()
    return cleaned_name


def main():
    """Define the base URL of the OGC API
    """
    base_url = "https://ospd.geolabs.fr:8300/ogc-api"
    
    # Get collections information
    collections_data = get_collections(base_url)
    # Convert JSON to GalaxyXML
    json_to_galaxyxml(collections_data)

if __name__ == "__main__":
    main()

