#!/usr/bin/python3
import argparse
import configparser
import json
import logging
import os
import subprocess

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
        with open('stdout', 'w') as f_out, open('stderr', 'w') as f_err:
            ret_code = subprocess.call(['/usr/bin/time', '-f', '%e, %U, %S', './binary'] + inputs, stdout=f_out, stderr=f_err)

        with open('stdout', 'r') as f_out, open('stderr', 'r') as f_err:
            stdout = f_out.read()
            stderr = f_err.read()

        # Extract the time information line.
        lines = stderr.splitlines()
        time_information = lines[-1].split(',')
        errors = '\n'.join(lines[:-1])

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


def main(config_file_path, exec_dir):
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
        inputs = pair[pair.find('[') +1 : pair.find(']')]
        inputs = inputs.split(',') if inputs else []
        output = pair[pair.find('\'') +1:pair.rfind('\'')]

        pairs.append((inputs, output))

    # We set the input/output pairs in the dictionary.
    testing['input_output'] = pairs

    # We start the testing flow.
    os.chdir(exec_dir)
    perform_tests(testing)


if __name__ == '__main__':
    # Parsing the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='The config file for the testcase.')
    parser.add_argument('exec_dir', help='The execution directory.')
    args = parser.parse_args()

    # Check if DEBUG mode is on or not.
    if "DEBUG" not in os.environ.keys() or os.environ["DEBUG"] == "True":
        # Debug setup to stdout and log file.
        logging.basicConfig(level=logging.DEBUG)
        rootLogger = logging.getLogger()

        fileHandler = logging.FileHandler(os.path.join(args.exec_dir, 'debug.log'), mode='w')
        logFormatter = logging.Formatter(DEBUG_FORMAT)
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)

    main(args.config_file, args.exec_dir)
