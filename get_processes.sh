#!/bin/bash

# Check if filename argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 {filename}"
    exit 1
fi

# Execute the Python script with the provided filename
python3 Processes/process_id.py --filename "$1"
