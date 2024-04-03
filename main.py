import requests
import json
import re
import galaxyxml.tool as gxt
import galaxyxml.tool.parameters as gxtp
from pprint import pprint
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree

def get_collections(base_url):
    """Define the path to the specific endpoint you want to access
    """
    endpoint = "/processes/OTB.BandMath"   
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
    
    
    pprint(json_data)
    print(json_data["id"])
    name_id = rename_tool(tool_name=json_data["id"])
    tool = gxt.Tool(name=name_id, id=json_data["id"], version=json_data["version"], description=json_data["title"], executable="dfsfsdfsfd")
    tool.help = (json_data["description"])
    pprint(json_data["inputs"])
    #pprint(tool.export())

def get_galaxyxml_inputs(inputs_json):


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

