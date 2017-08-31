"""
Module with utility functions.
"""
import re

def extract_function_name_from_section(section):
    """
    Method used to extract the function name of a section name.
    :param section: the section from which we will extract the function name.
    :return: the function name corresponding to this section or None if not found.
    """
    result = re.search('[^ ]*.text.([^ \n]*)', section)
    if result is not None:
        return result.group(1)