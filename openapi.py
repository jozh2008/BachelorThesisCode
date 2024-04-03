import yaml
import json

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


def main():
    content = parse("processes_OTB.BandMath.yml")
    pprint(content)

if __name__ == "__main__":
    main()
