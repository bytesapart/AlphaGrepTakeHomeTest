"""
Author: Osama Iqbal

"""

import sys
import os
import logging
import tempfile
import datetime
import argparse
import pandas as pd
import pysftp

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

    logger = logging.getLogger('position_reconciliation')
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
    if args.get('name') is None:
        raise ValueError("Name is needed for remoting to the machine")
    if args.get('configuration') is None:
        raise ValueError('No configuration file given to the script.')
    if not os.path.isfile(args.get('configuration')):
        raise FileNotFoundError('Configuration File not found')
    if args.get('directory') is None:
        raise ValueError('No directory file given to the script.')
    if not os.path.isfile(args.get('directory')):
        raise FileNotFoundError('directory File not found')
    if args.get('summary') is None:
        raise ValueError('No summary file given to the script')
    summary_files = args.get('summary').split(',')
    for f in summary_files:
        if not os.path.isfile(f):
            raise FileNotFoundError(f'No summary file {f} found')


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
    args['summary'] = args.get('summary').split(',')


def parse_args():
    """
    Parses the arguments given to the script
    Returns
    -------
    dictionary: A dictionary object containing the arguments passed
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("-n", "--name", help="The Name to reconcile positions for",
                        default=None, type=str)
    parser.add_argument("-c", "--configuration", help="The full path to configuration file",
                        default=None, type=str)
    parser.add_argument("-d", "--directory", help="The directory where one needs to upload this file",
                        default=None, type=str)
    parser.add_argument("-s", "--summary", help="Comma separated list of summary files",
                        default=None, type=str)

    return vars(parser.parse_args())


def bad_line(line):
    """
    Function to process any bad lines
    Parameters
    ----------
    line: list
        The delimiter separated list

    Returns
    -------
    list
        The final list
    """
    return line[:11]


def get_consolidated_summary_df(summary_files_list):
    """
    Get a list of consolidated summary file dataframes
    Parameters
    ----------
    summary_files_list: list
        List of summary files
    Returns
    -------
    pd.DataFrame
        A DataFrames
    """
    log.info("Consolidating Summary")
    consolidated_df = pd.DataFrame(columns=[0, 1, 3])
    for f in summary_files_list:
        consolidated_df = pd.concat([consolidated_df,
                                     pd.read_csv(f, header=None, delim_whitespace=True, on_bad_lines=bad_line,
                                                 engine='python')[[0, 1, 3]]],
                                    ignore_index=True)
    consolidated_df = consolidated_df.astype({3: float})
    consolidated_df.columns = ['LogfileName', 'Instrument', 'Position']
    return consolidated_df


def get_consolidated_position_on_log_files(name, summary_df, position_container):
    """
    Recon position based off of name
    Parameters
    ----------
    name: str
        Name to recon. on
    summary_df:
        The dataframe containing the data
    position_container:
        The position container to store recon. values in

    Returns
    -------
    None
    """
    log.info("Generating Consolidated positions dictionary")
    for index, row in summary_df.iterrows():
        if name.lower() in index[0].lower():
            if position_container.get(index[1]) is not None:
                position_container[index[1]] = position_container[index[1]] + row['Position']
            else:
                position_container[index[1]] = row['Position']


def generate_cfg_file(position_container, configuration):
    """
    Generate a temporary cfg file that needs to be SFTP'ed to the servers
    Parameters
    ----------
    position_container: dict
        The dictionary containing consolidated positions
    configuration:
        The configuration file that needs to be modified

    Returns
    -------
    str
        A string containing the file path to the new file
    """
    log.info("Generating Positions config file")
    tempdir = tempfile.gettempdir()
    with open(configuration, 'r') as config_file:
        config_file_container = config_file.readlines()

    with open(os.path.join(tempdir, 'PositionLimits.cfg'), 'w') as position_file:
        line_container = []
        for line in config_file_container:
            line_breakdown = line.split('_')
            instrument = '_'.join(line_breakdown[:4])
            value = float(line_breakdown[-1].split(' = ')[-1])
            type_of_pos = line_breakdown[-1].split(' = ')[0]

            if type_of_pos.lower() == 'maxlongpos' or type_of_pos.lower() == 'maxlongexposure':
                value = value - position_container[instrument]
            elif type_of_pos.lower() == 'maxshortpos' or type_of_pos.lower() == 'maxshortexposure':
                value = value + position_container[instrument]

            line_container.append(f'{instrument}_{type_of_pos} = {int(value)}\n')

        position_file.writelines(line_container)

    return os.path.join(tempdir, 'PositionLimits.cfg')


def generate_directory_config_dict(directory):
    """
    Generate Config dict
    Parameters
    ----------
    directory: str
        file path to directory config

    Returns
    -------
    dict
        config dictionary
    """
    config_dict = {}
    with open(directory, 'r') as cfg:
        lines = cfg.readlines()

    current_lookup = None
    for line in lines:
        if line.startswith('['):
            current_lookup = line[1:-2]
        if config_dict.get(current_lookup) is None and line.startswith('['):
            config_dict[current_lookup] = []
        elif line.startswith('/'):
            config_dict[current_lookup].append(line)

    return config_dict


def sftp_exists(sftp, path):
    try:
        sftp.stat(path)
        return True
    except FileNotFoundError:
        return False


def transfer_file_to_server(directory, position_config_file, name):
    """
    Transfer the file over to the remote server
    Parameters
    ----------
    directory: str
        Filename of the directory config
    position_config_file:
        Position Configuration file
    name:
        Name of the logfile

    Returns
    -------
    None
    """
    config_dictionary = generate_directory_config_dict(directory)
    for key, value in config_dictionary.items():
        for val in value:
            if name.lower() in val.lower():
                with pysftp.Connection(key, username='osama', private_key="Problem3\\id_rsa") as sftp:
                    if not sftp.exists(val.strip()):
                        raise FileNotFoundError(
                            f'Source path {val} does not exist. Please enter valid source path')
                    sftp.put(position_config_file, val.strip('\n') + 'PositionLimits.cfg')
        # print(items)


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
        validate_parameters(args)
        sanitise_args(args)

        summary_df = get_consolidated_summary_df(args.get('summary'))
        # Group the summary dfs by (LogfileName, Instrument) as the index, and sum up all the positions
        log.info("Grouping Summary and summing values")
        summary_df = summary_df.groupby(['LogfileName', 'Instrument']).sum()

        position_container = {}  # This is for summing up all the "instruments" for a particular log file
        # Iterate through DF and get consolidated positions
        get_consolidated_position_on_log_files(args.get('name'), summary_df, position_container)

        # Generate the cfg file
        position_config_file = generate_cfg_file(position_container, args.get('configuration'))

        #  SFTP/SCP the file onto the server
        transfer_file_to_server(args.get('directory'), position_config_file, args.get('name'))

    except Exception as error:
        log.exception(error)

    finally:
        logging.shutdown()


if __name__ == '__main__':
    # Initialize the logger
    log = init_logger()
    # Call the main function
    sys.exit(main())
