"""
Author: Osama Iqbal
There are 3 different ways this queue can be made, and all three modes are in the script.
Taking inspiration from classic compression algorithms and their modes, since there is no
'one-size-fits-all', we optimise for different sets (such as in compression, some might
need faster compress, some might need faster decompression, while others might need some
middle group based tweak). Therefore, even though there is a bonus for not replicating
the queue, I will implement both the ways, that replicating the queue and without it.

Therefore, the modes that this version queue runs in are:
1. COMPUTE (default): This mode computes the operations and hence, takes up less space (both
in memory in disk), but the tradeoff is that we spend compute cycles on it.
2. DISK: The entire queue is serialised and saved on disk. This is good when S3 bucket disk
space is super cheap, and can store large objects. Requires replication of the queue.
3. MEMORY: This is a compromise between DISK and COMPUTE. Not that fast,
but not that slow either. Again, requires replication of the queue.


1. Run the file by executing (python 3 required since f-strings are used!)
    ```python.exe 02_version_queue/main.py <number_of_inputs>```
    assuming your working directory is "AlphaGrepTakeHomeTest".
2. Then add the number of operations, followed by the operations on the screen.
"""
import copy
import sys
import os
import logging
import tempfile
import datetime
import pickle
from enum import Enum

log = None
queue = []
queue_state = {}  # For DISK and MEMORY states
tempdir = tempfile.mkdtemp(prefix=f'version_queue_pickle_{os.getpid()}_')


class Mode(Enum):
    COMPUTE = 1
    DISK = 2
    MEMORY = 3


def init_logger():
    """
    Initializes the logger
    Returns
    -------
    Logger object
    """
    tempdir = tempfile.mkdtemp(
        prefix=f'downloader_framework_{os.getpid()}__{datetime.datetime.now().strftime("%H_%M_%S")}')

    logger = logging.getLogger('version_queue')
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
    number_of_inputs = int(input())
    return [input() for i in range(number_of_inputs)]


def sanitise_args(args):
    """
    Sanitise the arguments given to the script.
    Parameters
    -------
    args: list
        List of arguments that need to be sanitised
    Returns
    -------
    list
    """
    return [tuple(element.split(' ')) for element in args]


def load_pickle_file():
    global queue_state
    global tempdir
    with open(os.path.join(tempdir, 'queue_state.pickle'), 'rb') as pf:
        queue_state = pickle.load(pf)


def save_pickle_file_and_clean_memory():
    global queue_state
    global tempdir
    with open(os.path.join(tempdir, 'queue_state.pickle'), 'wb') as pf:
        pickle.dump(queue_state, pf)
    queue_state = {}


def enqueue(element):
    global queue
    queue.append(element)


def dequeue():
    global queue
    popped_element, *queue = queue
    return popped_element


def print_noncompute(state):
    global queue_state
    log.info(f'The queue at version {state} is {queue_state[int(state)]}.')
    print(queue_state[int(state)])


def print_compute(args, state):
    global queue
    queue_copy = copy.deepcopy(queue)

    for element in reversed(args):
        if element[0] == 'e':
            queue_copy.pop()
        if element[0] == 'd':
            queue_copy.insert(0, element[1])
    log.info(f'The queue at version {state} is {queue_copy}.')
    print(queue_copy)


def process_queue_with_compute(args):
    """
    Process the queue with compute based helper function. Hence, if we encounter "Print" operations,
    we will compute the parameters and print them. Logic is quite simple. Just reverse the operations.
    Having said that the "d" operation does not contain the element which was in the lead, hence,
    every time we "dequeue" we create a modified args which contains the element that was dequeued. Then, every time
    we encounter a "p" we slice the array unto the state, and for every "e" we pop from the array, and for every "d",
    we insert the element to the front of the array.
    Parameters
    ----------
    args

    Returns
    -------

    """
    args_for_compute = []
    for i, element in enumerate(args):
        if element[0].lower() == 'e':
            enqueue(element[1])
            args_for_compute.append(element)
        elif element[0].lower() == 'd':
            dequeued_element = dequeue()
            args_for_compute.append((element[0], dequeued_element))
        elif element[0].lower() == 'p':
            print_compute(args_for_compute[int(element[1]):i], element[1])


def process_queue_with_disk(args):
    """
    Here, we pickle to a temporary location, and clear of the memory version queue. After every operation,
    we load the pickle file and
    Parameters
    ----------
    args:
        The list of arguments

    Returns
    -------
    None
    """
    global queue
    global queue_state
    save_pickle_file_and_clean_memory()
    for i, element in enumerate(args):
        load_pickle_file()
        if element[0].lower() == 'e':
            enqueue(element[1])
            queue_state[i + 1] = queue
            save_pickle_file_and_clean_memory()
        elif element[0].lower() == 'd':
            dequeued_element = dequeue()
            queue_state[i + 1] = queue
            save_pickle_file_and_clean_memory()
        elif element[0].lower() == 'p':
            print_noncompute(element[1])


def process_queue_with_memory(args):
    """
    Here, we use the state dictionary to perform all operations
    Parameters
    ----------
    args:
        The list of arguments

    Returns
    -------
    None
    """
    global queue
    global queue_state
    for i, element in enumerate(args):
        if element[0].lower() == 'e':
            enqueue(element[1])
            queue_state[i + 1] = queue
        elif element[0].lower() == 'd':
            dequeued_element = dequeue()
            queue_state[i + 1] = queue
        elif element[0].lower() == 'p':
            print_noncompute(element[1])


def process_queue(args, mode):
    """
    Process the queue
    Parameters
    ----------
    args: list
        List of arguments passed to the script
    mode:
        The mode to run the script in

    Returns
    -------
    None
    """
    if mode == Mode.COMPUTE:
        process_queue_with_compute(args)
    elif mode == Mode.DISK:
        process_queue_with_disk(args)
    elif mode == Mode.MEMORY:
        process_queue_with_memory(args)


def validate_args(args):
    """

    Parameters
    ----------
    args: list
        list of arguments given to the script

    Returns
    -------
    None
    """
    try:
        for element in args:
            if element[0] == 'p':
                int(element.split(' ')[1])
    except ValueError:
        raise ValueError('p must contain an integer as a version, and not an arbitrary string!')


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
        validate_args(args)
        args = sanitise_args(args)
        process_queue(args, Mode.COMPUTE)

    except Exception as error:
        log.exception(error)

    finally:
        logging.shutdown()


if __name__ == '__main__':
    # Initialize the logger
    log = init_logger()
    # Call the main function
    sys.exit(main())
