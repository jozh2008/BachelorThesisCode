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
    tool.inputs = create_params(inputs_json=json_data["inputs"], outputs_json = json_data["outputs"])
    #tool.outputs = create_output_param(output_json=json_data["outputs"])
    #pprint(json_data["inputs"])
    pprint(tool.export())

def create_text_param(param_name, param_dict):
    return gxtp.TextParam(
        name=param_name,
        label=param_dict["title"],
        help=param_dict["description"],
        optional=False,
    )

def create_select_param(param_name, param_dict):
    if param_dict["schema"].get("enum") is not None:
        data_types = param_dict["schema"]["enum"]
        data_types_dict = {data_type: data_type for data_type in data_types}
    else:
        print("To Do implement it")
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

def create_float_param(param_name, param_dict):
    default_value = param_dict["schema"].get("default", 0) if not param_dict["schema"].get("nullable") else None
    return gxtp.FloatParam(
        name=param_name,
        label=param_dict["title"],
        help=param_dict["description"],
        value=default_value
    )

def create_boolean_param(param_name, param_dict):
    default_value = param_dict["schema"].get("default", False)
    return gxtp.BooleanParam(
        name=param_name,
        label=param_dict["title"],
        help=param_dict["description"],
        checked=default_value
    )

def create_data_param(param_name, param_dict, param_extended_schema, isArray: bool):
    enum_values = []
    if isArray:
        extract_enum(param_extended_schema['items'], enum_values)
    else:
        extract_enum(param_extended_schema['oneOf'], enum_values)
    unique_enum_values = ','.join({value.split('/')[-1] for value in enum_values})
    return gxtp.DataParam(
        name=param_name,
        label=param_dict["title"],
        help=param_dict["description"],
        format=unique_enum_values
    )

def extract_enum(schema_item, enum_values):
    if 'enum' in schema_item:
        enum_values.extend(schema_item['enum'])
    elif 'properties' in schema_item:
        for prop in schema_item['properties'].values():
            extract_enum(prop, enum_values)
    elif 'oneOf' in schema_item:
        for option in schema_item['oneOf']:
            extract_enum(option, enum_values)
    elif 'allOf' in schema_item:
        for sub_item in schema_item['allOf']:
            extract_enum(sub_item, enum_values)

def create_params(inputs_json, outputs_json):
    inputs = gxtp.Inputs()
    
    for param_name, param_dict in inputs_json.items():
        param_schema = param_dict.get("schema")
        param_extended_schema = param_dict.get("extended-schema")
        param_type = param_schema.get("type")
        
        if param_type == "string":
            if param_schema.get("enum"):
                param = create_select_param(param_name, param_dict)
            else:
                param = create_text_param(param_name, param_dict)
        elif param_type == "integer":
            param = create_integer_param(param_name, param_dict)
        elif param_type == "number":
            param = create_float_param(param_name, param_dict)
        elif param_type == "boolean":
            param = create_boolean_param(param_name, param_dict)
        elif param_extended_schema is not None:
            is_array = param_extended_schema.get("type") == "array"
            param = create_data_param(param_name, param_dict, param_extended_schema, is_array)
        else:
            # Handle unsupported parameter types gracefully
            print(f"Warning: Parameter '{param_name}' with unsupported type '{param_type}'")
            continue
        
        inputs.append(param)
    
    

    return inputs

def create_output_param(output_json):
    






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

