import requests


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


def get_ids():
    processes_data = get_capabilities()
    process_ids = [process["id"] for process in processes_data["processes"]]
    # Specify the file path for the IDs
    ids_file_path = "process_ids_2.txt"

    # Write the IDs to the file
    with open(ids_file_path, "a+") as file:
        file.seek(0)
        lines = [line.strip() for line in file.readlines()]
        for process_id in process_ids:
            if process_id not in lines:
                file.write(process_id + "\n")
    file.close()


if __name__ == "__main__":
    get_ids()
