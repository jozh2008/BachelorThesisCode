import requests
import json
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
    root = Element('galaxy')
    for key, value in json_data.items():
        element = SubElement(root, key)
        if isinstance(value, dict):
            # If value is a nested object, recursively convert it
            element.append(json_to_galaxyxml(value))
        else:
            element.text = str(value)
    print(root)
    return root


def main():
    """Define the base URL of the OGC API
    """
    base_url = "https://ospd.geolabs.fr:8300/ogc-api"
    
    # Get collections information
    collections_data = get_collections(base_url)
    # Convert JSON to GalaxyXML
    galaxyxml_tree = json_to_galaxyxml(collections_data)

    # Convert ElementTree to string and save to file
    galaxyxml_string = tostring(galaxyxml_tree, encoding='utf-8').decode('utf-8')
    with open('processes_OTB.BandMath.xml', 'w') as xml_file:
        xml_file.write(galaxyxml_string)

if __name__ == "__main__":
    main()

