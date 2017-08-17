"""
Module which is the main entry point.
"""

import logging
import os
import configparser
import config
import executor.executor as executor

# Debugging format.
DEBUG_FORMAT = '%(levelname)s:%(filename)s:%(funcName)s:%(asctime)s %(message)s\n'


def main():
    logging.debug("Executing...")

    # First we read the config file.
    config_file = configparser.ConfigParser()
    config_file.read('config.ini')

    # We parse the config file into a custom config object.
    config_obj = config.Config(config_file)

    # Special testing mode for multiple executions.
    if config_obj.default["testmode"] is True:
        logging.debug("Testing mode activated!")

        # Type of operation in this case depends on the type of transformation.
        if config_obj.semantic_mod["type"] == "StructReordering":

            # Amounts to integer list conversion.
            amounts = config_obj.struct_reordering["amount"]
            amounts_ints = [x for x in amounts.split(",")]

            # For every amount we will execute an executor flow.
            for amount in amounts_ints:

                # We set the amount value.
                config_obj.struct_reordering["amount"] = amount

                # We create an executor to start the semantic renewability flow.
                executor_flow = executor.Executor(config_obj)

                # We start the execution.
                executor_flow.execute()

        elif config_obj.semantic_mod["type"] == "FPReordering":

            # Amounts to integer list conversion.
            amounts = config_obj.functionparam_reordering["amount"]
            amounts_ints = [x for x in amounts.split(",")]

            # For every amount we will execute an executor flow.
            for amount in amounts_ints:

                # We set the amount value.
                config_obj.functionparam_reordering["amount"] = amount

                # We create an executor to start the semantic renewability flow.
                executor_flow = executor.Executor(config_obj)

                # We start the execution.
                executor_flow.execute()
    else:

        # We create an executor to start the semantic renewability flow.
        executor_flow = executor.Executor(config_obj)

        # We start the execution.
        executor_flow.execute()

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
    main()
