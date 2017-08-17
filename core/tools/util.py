"""
Module with utility functions used within tools.
"""
import re


def handle_status(status, stdout, stderr):
    """
    Method used to handle faulty status codes of tools.
    (throws an exception)

    :param status: the status code of a command.
    :return: nothing.
    """
    # We check the status code.
    if int(status) != 0:
        raise Exception('Something went wrong, stdout: ' + str(stdout.decode()) + ' stderr: ' +
                        str(stderr.decode()))


def extract_function_name_from_section(section):
    """
    Method used to extract the function name of a section name.
    :param section: the section from which we will extract the function name.
    :return: the function name corresponding to this section or None if not found.
    """
    result = re.search('[^ ]*.text.([^ \n]*)', section)
    if result is not None:
        return result.group(1)