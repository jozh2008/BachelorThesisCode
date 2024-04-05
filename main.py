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
    #pprint(json_data)
    #print(json_data["id"])
    name_id = rename_tool(tool_name=json_data["id"])
    tool = gxt.Tool(name=name_id, id=json_data["id"], version=json_data["version"], description=json_data["title"], executable="dfsfsdfsfd")
    tool.help = (json_data["description"])
    tool.inputs = create_params(inputs_json=json_data["inputs"])
    #pprint(json_data["inputs"])
    pprint(tool.export())

"""
def get_galaxyxml_inputs(inputs_json):
    inputs = gxtp.Inputs()
    #print(inputs_json)
    for param_name, param_dict in inputs_json.items():
        param_schema = param_dict.get("schema")
        if param_schema.get("type") == "string":
            if param_schema.get("enum") is None:
                param = gxtp.TextParam(name=param_name,label=param_dict["title"], help=param_dict["description"],optional=False)
                param.space_between_arg = " "
                inputs.append(param)
            else:
                print()
                data_types = param_schema.get("enum")
                print(data_types)
                data_types_dict = {data_type: data_type for data_type in data_types}
                param = gxtp.SelectParam(name = param_name, default=param_schema["default"],label=param_dict["title"], help=param_dict["description"], options=data_types_dict)
                param.space_between_arg = " "
                inputs.append(param)
        elif param_schema.get("type") == "integer":
            if param_schema.get("default") is None and param_schema.get("nullable") is None:
                param = gxtp.IntegerParam(name=param_name, label=param_dict["title"],help=param_dict["description"], value=0)
                inputs.append(param)
            elif param_schema.get("default") is None:
                param = gxtp.IntegerParam(name=param_name, label=param_dict["title"],help=param_dict["description"])
                inputs.append(param)
            else:
                param = gxtp.IntegerParam(name=param_name, label=param_dict["title"],help=param_dict["description"], value=param_schema["default"])
                inputs.append(param)
            
    #pprint(inputs)
    return inputs
"""

def create_text_param(param_name, param_dict):
    return gxtp.TextParam(
        name=param_name,
        label=param_dict["title"],
        help=param_dict["description"],
        optional=False,
    )

def create_select_param(param_name, param_dict):
    data_types = param_dict["schema"]["enum"]
    data_types_dict = {data_type: data_type for data_type in data_types}
    return gxtp.SelectParam(
        name=param_name,
        default=param_dict["schema"].get("default"),
        label=param_dict["title"],
        help=param_dict["description"],
        options=data_types_dict,
    )

def create_integer_param(param_name, param_dict):
    default_value = param_dict["schema"].get("default", 0) if not param_dict["schema"].get("nullable") else None
    return gxtp.IntegerParam(
        name=param_name,
        label=param_dict["title"],
        help=param_dict["description"],
        value=default_value
    )

def create_params(inputs_json):
    inputs = gxtp.Inputs()
    for param_name, param_dict in inputs_json.items():
        param_schema = param_dict.get("schema")
        param_type = param_schema.get("type")

        if param_type == "string":
            if param_schema.get("enum") is None:
                param = create_text_param(param_name, param_dict)
            else:
                param = create_select_param(param_name, param_dict)
        elif param_type == "integer":
            param = create_integer_param(param_name, param_dict)
        else:
            continue  # Skip unsupported types
        
        inputs.append(param)

    return inputs



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

