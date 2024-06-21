import requests
import sys
import os


def get_capabilities():
    # Extract all process IDs

    try:
        # Make a GET request to retrieve information about available collections
        response = requests.get("https://ospd.geolabs.fr:8300/ogc-api/processes")
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

        # Extract the JSON data from the response
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        print("Failed to retrieve collections:", e)
        return None


def get_ids(file: str):
    processes_data = get_capabilities()
    if processes_data is None:
        return
    process_ids = [process["id"] for process in processes_data["processes"]]
    # Specify the file path for the IDs
    ids_file_path = check_direcotry()

    # Write the IDs to the file
    with open(ids_file_path, "a+") as file:
        file.seek(0)
        lines = [line.strip() for line in file.readlines()]
        for process_id in process_ids:
            if process_id not in lines:
                file.write(process_id + "\n")
    file.close()


def check_direcotry():
    cwd = os.getcwd()

    # Check if we are already in the Processes directory
    if os.path.basename(cwd) != "Processes":
        # Ensure the Processes directory exists
        os.makedirs("Processes", exist_ok=True)
        ids_file_path = os.path.join("Processes", f"{file}.txt")
    else:
        ids_file_path = f"{file}.txt"

    return ids_file_path


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "--filename":
        print("Error: File not provided. Use python3 process_id.py --filename {filename}.txt")
        sys.exit(1)
    file = sys.argv[2]
    get_ids(file=file)
