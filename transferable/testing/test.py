import logging
import os
import configparser
import json
import sys

from subprocess import Popen, PIPE

# Debugging format.
DEBUG_FORMAT = '%(levelname)s:%(filename)s:%(funcName)s:%(asctime)s %(message)s\n'


def perform_tests(testing):

    # Dictionary used to store all relevant test data.
    data = dict()
    data['results'] = []

    # We iterate over all input/output pairs.
    for idx, pair in enumerate(testing['input_output']):

        # Used to index the JSON data.
        idx = str(idx)
        data_entry = dict()

        # Unpack inputs/output tuple.
        (inputs, output) = pair

        # Debug information.
        logging.debug('Input: ' + str(inputs))
        logging.debug('Expected output: ' + str(output))

        # We generate the command to be executed.
        command_exec = ['/usr/bin/time', '-f', '%e, %U, %S', './d.out'] + inputs

        # We execute the command
        ret_code, stdout, stderr = execute_command_status_output(command_exec)

        # Decode output and error
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")

        # Extract the time information line.
        time_information = stderr.split('\n')[-2:][0].split(',')
        errors = '\n'.join(stderr.split('\n')[:-2])

        # We store the return code.
        data_entry['return_code'] = ret_code

        # We store possible errors.
        data_entry['stderr'] = errors

        # Parse the real output
        data_entry['input'] = ' '.join(inputs)
        data_entry['output'] = stdout
        data_entry['expected_output'] = output
        if ret_code == 0 and stdout == output:
            data_entry['correct'] = True
        else:
            data_entry['correct'] = False

        # Process time information
        data_entry['time'] = dict()
        data_entry['time']['real'] = time_information[0]
        data_entry['time']['user'] = time_information[1]
        data_entry['time']['system'] = time_information[2]

        # We add the data entry to the results
        data['results'].append(data_entry)

    # We dump the results in json format.
    with open('results.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False)


def execute_command_status_output(command, out=PIPE):
    logging.debug("Executing command: " + str(" ".join(command)))

    # Command execution itself.
    p = Popen(command, stdout=out if out is not None else PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    ret_code = p.returncode
    logging.debug("ret code: " + str(ret_code))
    if stdout is not None:
        logging.debug("stdout: " + stdout.decode("utf-8"))
    if stderr is not None:
        logging.debug("stderr: " + stderr.decode("ascii"))
    return ret_code, stdout, stderr


def main(config_file_path):
    logging.debug("Executing...")

    # First we read the config file.
    config_file = configparser.ConfigParser()
    config_file.read(config_file_path)

    # We parse the config file into a custom config object.
    testing = dict()
    input_output = json.loads(config_file.get("TESTING", "InputOutput"))

    # Parse the input/output pairs.
    pairs = []
    for pair in input_output:
        parts = pair.split("],'")

        inputs = [x for x in parts[0][1:].split(',')]
        output = parts[1][:-1]

        pairs.append((inputs, output))

    # We set the input/output pairs in the dictionary.
    testing['input_output'] = pairs

    # We start the testing flow.
    perform_tests(testing)


def _parse_args(input_args):
    """
    Function used to parse the arguments of this script.
    """
    if not len(input_args) in (2,):
        print('Usage: python3 main.py <config_file>')
        return
    return sys.argv[1]

# Parse the arguments.
if __name__ == '__main__':

    # Check if DEBUG mode is on or not.
    if "DEBUG" not in os.environ.keys() or os.environ["DEBUG"] == "True":

        # Debug setup to stdout and log file.
        logging.basicConfig(level=logging.DEBUG)
        logFormatter = logging.Formatter(DEBUG_FORMAT)
        rootLogger = logging.getLogger()

        fileHandler = logging.FileHandler("debug.log", mode='w')
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)

    # Start the execution.
    args = sys.argv
    arguments = _parse_args(args)
    if arguments:
        main(arguments)

