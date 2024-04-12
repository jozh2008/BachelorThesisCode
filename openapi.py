#!/usr/bin/env python3
#print("This is a placeholder function.")

import sys


def print_inputs():
    print("This is a placeholder function.")
    # Get command-line arguments
    args = sys.argv[1:]  # Exclude the first argument which is the script name
    attributes = convert(args=args)
    
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

def convert(args):
    it = iter(args)
    res_dict = dict(zip(it,it))
    return res_dict

if __name__ == "__main__":
    print_inputs()
