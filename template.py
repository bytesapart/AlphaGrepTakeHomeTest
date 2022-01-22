"""
Author: Osama Iqbal
This particular file is the crux of the downloader framework.

The assumption here is that the configuration would be provided on the command line,
though there is a provision of making a JSON file consisting of key/values that will be
parsed for taking the parameters to run the script.

There is another assumption, since the 4th point in the question states a "Time Window".
The assumption is that this script will run perpetually, and

1. Run the file by executing
    ```python.exe 01_downloader_framework/main.py -i <ip_address> -u <username> -p <password> -s <source_path> -d <destination_path> -t <time_in_24_hr_format>```
    assuming your working directory is "AlphaGrepTakeHomeTest"
2. There are other optional parameters, like ```-n <True/False>``` which stands for "nested", that
is, whether to download sub-folders or not.
3. ```-t``` parameter is also optional, if not provided, the script starts running immidiately
4. ```-j <path_to_json_file>``` one can use the -j parameter to pass in a JSON file with the keys and values
    as
    ```
   {
     "ip_address": 127.0.0.1,
     "username" : "the_username",
     "password": "the_password",
     "timestamp": "17:30",
     "nested": true,
     "source_path": "/source/path",
     "destination_path": "/destination/path"
   }
   ```

"""

import sys
import os
import logging
import tempfile
import datetime
import argparse
import json

log = None


def init_logger():
    """
    Initializes the logger
    Returns
    -------
    Logger object
    """
    tempdir = tempfile.mkdtemp(
        prefix=f'downloader_framework_{os.getpid()}__{datetime.datetime.now().strftime("%H_%M_%S")}')

    logger = logging.getLogger('downloader_framework')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(os.path.join(tempdir, 'logfile.log'))
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(filename)s:%(lineno)s - %(funcName)20s() - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


def parse_args():
    """
    Parses the arguments given to the script
    Returns
    -------
    dictionary: A dictionary object containing the arguments passed
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("-i", "--ip_address", help="The IP Address to connect to",
                        default=None, type=str)
    parser.add_argument("-u", "--username", help="The username used in order to connect",
                        default=None, type=str)
    parser.add_argument("-p", "--password", help="The password used in order to connect",
                        default=None, type=str)
    parser.add_argument("-s", "--source_path", help="The source path",
                        default=None, type=str)
    parser.add_argument("-d", "--destination_path", help="The destination path",
                        default=None, type=str)
    parser.add_argument("-t", "--time_to_begin", help="The timestamp on when to begin",
                        default=None, type=str)
    parser.add_argument("-n", "--nested_config", help="Whether to download nested folders or not",
                        default=None, type=str)
    parser.add_argument("-j", "--json_config", help="JSON file containing the configuration",
                        default=None, type=str)

    return vars(parser.parse_args())


def main():
    """
    The main function of the program containing the business logic
    Returns
    -------
    int: Returns 0 if program runs successfully, or returns 1
    """
    try:
        log.info("Starting main() function")
        # ===== Step 1: Get all the parameters from the console =====
        args = parse_args()

        if args.get('json_config') is not None:
            # We parse the JSON file for getting the configurations
            with open(args.get('json_config')) as f:
                args = json.load(f)

    except Exception as error:
        log.exception(error)


if __name__ == '__main__':
    # Initialize the logger
    log = init_logger()
    # Call the main function
    sys.exit(main())
