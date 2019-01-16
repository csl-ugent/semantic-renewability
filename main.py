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
import sys
import traceback

import executor.executor as executor

# Debugging format.
DEBUG_FORMAT = '%(levelname)s:%(filename)s:%(funcName)s:%(asctime)s %(message)s\n'

def main(mode, number_of_seeds, numbers_of_versions, seed, testmode, transformation_type):
    logging.debug('Executing...')

    # Change the directory
    os.chdir(os.path.dirname(sys.argv[0]))

    # First we read and parse the config file.
    config_file = configparser.ConfigParser()
    config_file.read('config.ini')
    config_obj = config.Config(config_file)

    if transformation_type:
        config_obj.semantic_mod['type'] = transformation_type

    # Convert the nr_of_versions option or argument into a list of numbers
    numbers_of_versions = numbers_of_versions if numbers_of_versions else config_obj.default['nr_of_versions']
    numbers_of_versions = [x for x in numbers_of_versions.split(',')]

    # If multiple seeds were requested we start at the first seed and continue until we have
    # the number of requested seeds. Every run is saved to a separate directory. The starting
    # seed can be overriden when a specific other seed was requested. If no multiple seeds
    # were requested we run once and use no separate directories.
    seed = seed if seed else int(config_obj.semantic_mod['seed'])
    seeds = range(seed, seed + number_of_seeds) if number_of_seeds else [seed]

    output_dir_config = config_obj.default['output_directory']
    shutil.rmtree(output_dir_config, True)
    for seed in seeds:
        config_obj.semantic_mod['seed'] = str(seed)

        # For every item we will execute an executor flow.
        for number_of_versions in numbers_of_versions:
            # We set the number of versions
            config_obj.default['nr_of_versions'] = number_of_versions

            # Set and create the output directory
            output_dir = os.path.join(output_dir_config, str(seed) if len(seeds) > 1  else '', str(number_of_versions) if len(numbers_of_versions) > 1 else '')
            config_obj.default['output_directory'] = output_dir
            shutil.rmtree(output_dir, True)
            os.makedirs(output_dir)

            # We create an executor to start the semantic renewability flow.
            executor_flow = executor.Executor(config_obj)

            print('************************ Generating ' + str(number_of_versions) + ' version(s) for seed ' + str(seed) + ' **********************')
            try:
                result = True
                executor_flow.execute(mode, testmode)
            except KeyboardInterrupt:
                raise
            except:
                result = False
                traceback.print_exc()
                pass

            # Output result
            print('************************ Result for seed ' + str(seed) + ': ' + str(result) + ' ************************')
            print()

# Parse the arguments.
if __name__ == '__main__':
    # Parsing the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debugging log.')
    parser.add_argument('-m', '--mode', type=int, default=2, help='The mode in which the framework is to be executed.')
    parser.add_argument('-n', '--number_of_seeds', type=int, help='The number of seeds to test.')
    parser.add_argument('-s', '--seed', type=int, help='The seed.')
    parser.add_argument('-t', '--testmode', type=int, default=0, help='The mode in which testing is to happen. 0 is no testing.')
    parser.add_argument('-v', '--numbers_of_versions', type=str, help='The numbers of versions to test.')
    parser.add_argument('-y', '--transformation_type', type=str, help='The type of transformation.')
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
    main(args.mode, args.number_of_seeds, args.numbers_of_versions, args.seed, args.testmode, args.transformation_type)
