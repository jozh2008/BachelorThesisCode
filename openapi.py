#!/usr/bin/env python3
#print("This is a placeholder function.")

import sys
# from galaxytools_workflow import GalaxyWorkflow

class Api:
    def __init__(self, server, api_key) -> None:
        self.server = server
        self.api_key = api_key


    def print_inputs(self):
        print("This is a placeholder function.")
        # Get command-line arguments
        args = sys.argv[1:]  # Exclude the first argument which is the script name
        attributes = self.convert(args=args)
        #gi = GalaxyWorkflow(server=self.server, api_key=self.api_key)
        #gi.get_all_histories()
        #gi.get_datasets_in_history()
        # Access attributes
        il = attributes.get('il')
        out = attributes.get('out')
        ram = attributes.get('ram')
        exp = attributes.get('exp')
        output_type_1 = attributes.get('output_type_1')

        # Use attributes as needed
        print("Input IL:", il)
        print("Output:", out)
        print("RAM:", ram)
        print("Experiment:", exp)
        print("Output Type 1:", output_type_1)

    def convert(self, args):
        it = iter(args)
        res_dict = dict(zip(it,it))
        return res_dict
    
    def output_json(self, mediaType, transmissionMode):
        output_format = {
            "outputs": {
                "result": {
                    "format": {
                        "mediaType": mediaType
                    },
                    "transmissionMode": transmissionMode
                }
            }
        }
        return output_format



if __name__ == "__main__":
    api = Api(server="http://127.0.0.1:9090/", api_key="")
    api.print_inputs()
