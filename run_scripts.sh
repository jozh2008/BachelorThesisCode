#!/bin/bash

# Check if file path is provided as a command-line argument
if [ $# -lt 1 ]; then
    echo "Error: File path not provided."
    echo "Usage: $0 <process ids file>"
    exit 1
fi

file_path=$1

# Check if file exists
if [ ! -f "$file_path" ]; then
    echo "Error: File '$file_path' not found."
    exit 1
fi

# Loop through each line in the file and pass it to main.py using --process option
while IFS= read -r line; do
    # Run the Python script with --process option and passing the current line as argument
    python3 GeneratorXML/main.py --process "$line"
done < "$file_path"
