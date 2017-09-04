#!/usr/bin/python3

"""
Module which is the main entry point.
"""

import argparse
import config
import configparser
import logging
import os
import shutil

import executor.executor as executor

# Debugging format.
DEBUG_FORMAT = '%(levelname)s:%(filename)s:%(funcName)s:%(asctime)s %(message)s\n'

def main(mode, testmode):
    logging.debug('Executing...')

    # First we read and parse the config file.
    config_file = configparser.ConfigParser()
    config_file.read('config.ini')
    config_obj = config.Config(config_file)

    # Conver the nr_of_versions option into a list of numbers
    numbers = [x for x in config_obj.default['nr_of_versions'].split(',')]

    # For every item we will execute an executor flow.
    output_dir_config = config_obj.default['output_directory']
    for number in numbers:
        # We set the number of versions
        config_obj.default['nr_of_versions'] = number

        # Set and create the output directory
        output_dir = output_dir_config if len(numbers) == 1 else os.path.join(output_dir_config, str(number))
        config_obj.default['output_directory'] = output_dir
        shutil.rmtree(output_dir, True)
        os.makedirs(output_dir)

        # We create an executor to start the semantic renewability flow.
        executor_flow = executor.Executor(config_obj)
        executor_flow.execute(mode, testmode)

# Parse the arguments.
if __name__ == '__main__':
    # Parsing the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debugging log.')
    parser.add_argument('-m', '--mode', type=int, default=2, help='The mode in which the framework is to be executed.')
    parser.add_argument('-t', '--testmode', type=int, default=0, help='The mode in which testing is to happen. 0 is no testing.')
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
    main(args.mode, args.testmode)
