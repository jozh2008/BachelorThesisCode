# Integration of the ZOO-Project into the Galaxy platform

In this repository will be my code stored.
Start date: 29.04.2024
End date: 29.07.2024

## How to run
The software requires Python 3.10. To check your Python version, run:



    $ python -V
    Python 3.10.12

Step 1: `python3 Processes/process_id.py --filename {filename}`, If file doesn't exist it creates a new file and include all process from the `https://ospd.geolabs.fr:8300/swagger-ui/oapip/#/GetCapabilities/get_processes`

Step 2: `sh run_scripts.sh FILE_PATH`

The result is a Galaxy XML files for each process that was in the process file.






