# Integration of the ZOO-Project into the Galaxy platform

In this repository will be my code stored.
Start date: 29.04.2024
End date: 29.07.2024

## How to run
The software requires Python 3.10. To check your Python version, run:



    $ python -V
    Python 3.10.12

Step 1:
    `sh get_processes.sh FILE_NAME`


    
If the file specified by FILE_NAME does not exist, a new file will be created containing all processes from the ZOO-Project GetCapabilities(`https://ospd.geolabs.fr:8300/swagger-ui/oapip/#/GetCapabilities/get_processes`)
 endpoint.
If the file exists, the script will add any new processes from the ZOO-Project GetCapabilities endpoint to the existing file.

Step 2: `sh run_scripts.sh FILE_PATH`

Sure! Here's the complete README file:

markdown

# Integration of the ZOO-Project into the Galaxy Platform

## Project Repository
Your code will be stored in this repository.

**Start Date:** 29.04.2024  
**End Date:** 29.07.2024

## How to Run

### Prerequisites
Ensure you have Python 3.10 installed. You can check your Python version by running:

```bash
$ python -V
Python 3.10.12

Steps

Step 1: Fetch Processes

Run the following command to fetch processes:

bash

sh get_processes.sh FILE_NAME

    If the file specified by FILE_NAME does not exist, a new file will be created containing all processes from the ZOO-Project GetCapabilities endpoint.
    If the file exists, the script will add any new processes from the ZOO-Project GetCapabilities endpoint to the existing file.

Step 2: Generate Galaxy XML Files

Run the following command to generate Galaxy XML files:

bash

sh run_scripts.sh FILE_PATH

This command will generate Galaxy XML files for each process listed in the specified process file.





