#!/usr/bin/python3

"""
Module which is the main entry point.
"""

import argparse
import config
import configparser
import logging
import os

import executor.executor as executor

# Debugging format.
DEBUG_FORMAT = '%(levelname)s:%(filename)s:%(funcName)s:%(asctime)s %(message)s\n'

def main(test_versions):
    logging.debug('Executing...')

    # First we read and parse the config file.
    config_file = configparser.ConfigParser()
    config_file.read('config.ini')
    config_obj = config.Config(config_file)

    # Add extra options
    config_obj.default['test_versions'] = test_versions

    # Special testing mode for multiple executions.
    if config_obj.default['testmode']:
        logging.debug('Testing mode activated!')

        # Convert the option into a list of numbers
        numbers = [x for x in config_obj.default['nr_of_reorderings'].split(',')]

        # For every item we will execute an executor flow.
        for number in numbers:
            # We set the number of reorderings
            config_obj.default['nr_of_reorderings'] = numbers

            # We create an executor to start the semantic renewability flow.
            executor_flow = executor.Executor(config_obj)
            executor_flow.execute()

    else:
        # We create an executor to start the semantic renewability flow.
        executor_flow = executor.Executor(config_obj)
        executor_flow.execute()

# Parse the arguments.
if __name__ == '__main__':
    # Parsing the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debugging log.')
    parser.add_argument('-t', '--test', action='store_true', help='Also test the protected binaries with the testing framework provided.')
    args = parser.parse_args()

    # Check if DEBUG mode is on or not.
    if args.debug:
        # Debug setup to stdout and log file.
        logging.basicConfig(level=logging.DEBUG)
        logFormatter = logging.Formatter(DEBUG_FORMAT)
        rootLogger = logging.getLogger()

        fileHandler = logging.FileHandler('debug.log', mode='w')
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)

    # Start the execution.
    main(args.test)
