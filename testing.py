import yaml
import json
import requests
from pprint import pprint

from openapi_parser import parse

def converter():
    # Open the JSON file
    with open('processes_OTB.BandMath.json', 'r') as json_file:
        # Load JSON content
        json_content = json.load(json_file)

    # Convert JSON to YAML
    yaml_content = yaml.dump(json_content)

    with open('processes_OTB.BandMath.yml', 'w') as yaml_file:
        yaml_file.write(yaml_content)

def write_id_to_file(file):
    with open(file, 'r') as json_file:
        # Load JSON content
        parsed_data = json.load(json_file)
    
    # Open file to write IDs
    with open('ids.txt', 'w') as file:
        # Loop through each process
        for process in parsed_data['processes']:
            # Extract ID and write it to the file
            process_id = process['id']
            file.write(process_id + '\n')

def get_collections(base_url, endpoint):
    """Define the path to the specific endpoint you want to access
    """  
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


def get_url(base_url, endpoint):
    """Define the path to the specific endpoint you want to access
    """  
    # Construct the full URL
    url = base_url + endpoint + ".html"
    return url

def main():
    base_url = "https://ospd.geolabs.fr:8300/ogc-api/processes/"
    collections_data_list = []
    # Open file to read IDs
    with open('ids.txt', 'r') as file:
        # Iterate over each line in the file
        for line in file:
            # Process the ID by calling get_collections
            id = line.strip()  # .strip() removes any leading/trailing whitespace and newline characters
            collections_data = get_url(base_url, id)
            if collections_data:
                collections_data_list.append(collections_data)

    # Write collections_data_list to a JSON file
    with open('all_url.txt', 'w') as txt_file:
        for item in collections_data_list:
            txt_file.write(str(item)+"\n")




    #content = parse("processes_OTB.BandMath.yml")
    #pprint(content)
    #write_id_to_file(file="processes.json")

if __name__ == "__main__":
    main()
