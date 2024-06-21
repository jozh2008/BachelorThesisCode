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

The result is a Galaxy XML files for each process that was in the process file.






