"""
Author: Osama Iqbal

1. Run the file by executing
    ```python.exe 01_downloader_framework/main.py -i <ip_address> -u <username> -p <password> -s <source_path> -d <destination_path> -t <time_in_24_hr_format-end_time_period>```
    assuming your working directory is "AlphaGrepTakeHomeTest"
2. ```-t``` parameter is also optional, if not provided, the script starts running immediately. When provided without a "-"
it will default run for 1 hour. Else, the "-" will be split upon by the code to get start and end times.
3. ```-j <path_to_json_file>``` one can use the -j parameter to pass in a JSON file with the keys and values
    as
    ```
   {
   "ip_address": "127.0.0.1",
   "username" : "osama",
   "password": "some_random_password",
   "time_window": "15:51-16:46",
   "source_path": "/home/osama/Downloads",
   "destination_path": "C:\\Users\\iqbal\\New Folder"
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
import time
import pysftp
import stat

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
    parser.add_argument("-t", "--time_window", help="The timestamp on when to begin and end",
                        default=None, type=str)
    parser.add_argument("-j", "--json_config", help="JSON file containing the configuration",
                        default=None, type=str)

    return vars(parser.parse_args())


def validate_parameters(args):
    """
    This function validates the parameters passed to the script
    Parameters
    ----------
    args: dict
        Contains a dictionary of all the parameters that are needed to run the script.

    Returns
    -------
    None
        if everything is valid return None, else returns False

    """
    log.info("Validating parameters")
    if args.get('ip_address') is None:
        raise ValueError("IP Address is needed for remoting to the machine")
    if args.get('username') is None:
        raise ValueError('No username given to the script. Username required for SSH/SFTP')
    if args.get('password') is None:
        raise ValueError('No password given to the script. Password required for SSH/SFTP')
    if args.get('source_path') is None:
        raise ValueError('Source path must be given to copy the files from')
    if args.get('destination_path') is None:
        raise ValueError('Destination path must be given to copy the file to')
    if not os.path.isdir(args.get('destination_path')):
        raise FileNotFoundError(
            f'The folder, {args.get("destination_path")} does not exist on local machine. Please create the folder')
    if args.get('time_window') is None:
        raise ValueError('Time window must be given to the script')


def sanitise_args(args):
    """
    Sanitises the args that are passed to the script

    Parameters
    ----------
    args: dict
        The argument dictionary which the script runs on

    Returns
    -------
    None
    """
    log.info("Sanitising Arguments ")
    if len(args.get('time_window')) != 2:
        args['time_window'] = args['time_window'].split('-')
        args['time_window'][0] = datetime.datetime.strptime(
            datetime.datetime.now().strftime('%D') + ' ' + args['time_window'][0],
            '%m/%d/%y %H:%M')
        args['time_window'][1] = datetime.datetime.strptime(
            datetime.datetime.now().strftime('%D') + ' ' + args['time_window'][1],
            '%m/%d/%y %H:%M')
    else:
        raise ValueError(
            "time_window must be of size 2, that is, it should contain 1 start element and one end element")


def start_fetch_from_remote_server(args):
    """

    Parameters
    ----------
    args: dict
        The arguments that the entire script runs on

    Returns
    -------
    None
    """
    log.info('Running start_fetch_from_remote_server')
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(args['ip_address'], username=args['username'], password=args['password'],
                           cnopts=cnopts) as sftp:
        # Check if remote path exists on the server or not
        if not sftp.exists(args['source_path']):
            raise FileNotFoundError(f'Source path {args["source_path"]} does not exist. Please enter valid source path')

        # Here, I have deliberately kept the while inside to avoid creation and deletion of the sftp object
        # Loads of sftp connections over time will overwhelm the server!
        while True:
            start_fetch_from_remote_server_core(sftp, args['source_path'], args['destination_path'])

            if (args['time_window'][1] - datetime.datetime.now()).days == -1:
                # If we have crossed the window, break the while loop
                log.info('Breaking out of loop, since time window has elapsed.')
                break
            else:
                # A healthy poll of 10 seconds
                log.info('Sleeping for 10 seconds before polling.')
                time.sleep(10)


def start_fetch_from_remote_server_core(sftp, source_path, destination_path):
    """
    Core function that has the business logic for fetching everything from the server
    Parameters
    ----------
    sftp: pysftp.Connection:
        The SFTP connection object
    source_path: str
        The source path where the files are stored
    destination_path: str
        The destination path where the files are stored

    Returns
    -------
    None
    """
    sftp.cwd(source_path)
    for f in sftp.listdir_attr():
        if not stat.S_ISDIR(f.st_mode):
            log.info(f'Checking {f.filename}')
            local_file_path = os.path.join(destination_path, f.filename)
            if (not os.path.isfile(local_file_path)) or (f.st_mtime > os.path.getmtime(local_file_path)):
                log.info(f'File {f.filename} is different or modified.')
                log.info(f'Downloading {f.filename}')
                sftp.get(f.filename, local_file_path)
        elif stat.S_ISDIR(f.st_mode):
            # check if local directory exists, if not, then make it
            if not os.path.isdir(os.path.join(destination_path, f.filename)):
                os.mkdir(os.path.join(destination_path, f.filename))
            destination_path = os.path.join(destination_path, f.filename)
            start_fetch_from_remote_server_core(sftp, f.filename, destination_path)


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

        validate_parameters(args)
        sanitise_args(args)

        # ===== Step 2: Perform sleep or fetch beased on the time =====
        timedel = args['time_window'][0] - datetime.datetime.now()

        # Check if delta is negative, if so, check if end time is also negative. If so, raise invalid time error,
        # else, if we are still in the timeframe, run the script
        if timedel.days < 0 and (args['time_window'][1] - datetime.datetime.now()).days < 0:
            raise ValueError(
                'Start time or End Time in the time window is less than the current time. '
                'Window has passed. Please enter appropriate timing')
        elif timedel.days < 0 and (args['time_window'][1] - datetime.datetime.now()).days == 0:
            # This means we are in the time window itself, and start running the script
            log.info(
                f'Start time is {args["time_window"][0]} and end time is {args["time_window"][1]}. Current time is '
                f'{datetime.datetime.now()}. Running fetch')
            start_fetch_from_remote_server(args)
        elif timedel.days == 0 and (args['time_window'][1] - datetime.datetime.now()).days == 0:
            # This means we need to start at a future timing
            log.info(
                f'Start time is {args["time_window"][0]} and end time is {args["time_window"][1]}. Current time is '
                f'{datetime.datetime.now()}. Sleeping main thread for {timedel.total_seconds()} seconds.')
            time.sleep(timedel.total_seconds())
            log.info(
                f'Start time is {args["time_window"][0]} and end time is {args["time_window"][1]}. Current time is '
                f'{datetime.datetime.now()}. Running fetch')
            start_fetch_from_remote_server(args)
        else:
            # Raise a value error. This also prevents a person from using "the next day" since that is the
            # assumption that this script has to run for the same day
            raise ValueError(
                'Script scheduled for the next day. Please make sure that the script is scheduled for same day.')

        log.info('Time window has elapsed. Ending script!')

    except Exception as error:
        log.exception(error)

    finally:
        logging.shutdown()


if __name__ == '__main__':
    # Initialize the logger
    log = init_logger()
    # Call the main function
    sys.exit(main())
