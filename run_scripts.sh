#!/bin/bash

# Function to check if the virtual environment is active
is_venv_active() {
    if [ -z "$VIRTUAL_ENV" ]; then
        return 1  # False
    else
        return 0  # True
    fi
}

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

# Ensure virtual environment is active
if ! is_venv_active; then
    echo "Virtual environment is not activated. Running 'make all' to set it up."
    make all
    if [ $? -ne 0 ]; then
        echo "Error: Failed to set up virtual environment."
        exit 1
    fi

    # Activate the virtual environment
    if [ -d ".venv/bin" ]; then
        # For Unix or MacOS
        . .venv/bin/activate
    elif [ -d ".venv/Scripts" ]; then
        # For Windows
        source .venv/Scripts/activate
    else
        echo "Error: Virtual environment not found."
        exit 1
    fi
else
    echo "Virtual environment is already activated."
fi

# Loop through each line in the file and pass it to main.py using --process option
while IFS= read -r line; do
    # Run the Python script with --process option and passing the current line as argument
    python3 main.py --process "$line"
done < "$file_path"
