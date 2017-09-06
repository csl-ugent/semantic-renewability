"""
Module used for parser related functionality.
"""
import logging
import re

class Parser:
    """
    Class used for parsing input files using a parse function
    the output is returned and can be written away to an output file.
    """

    @staticmethod
    def parse_file(input_file, parse_function, output_file=None):

        # Debug
        logging.debug("Parsing file: " + input_file + "...")

        # The result of the parser.
        output_lines = []

        # We open the file for reading.
        with open(input_file, "r") as fp:

            # We iterate over all lines within the input file
            # and apply the parse function to each line to
            # generate output.
            for line in fp:
                parsed_output = parse_function(line)
                if parsed_output is not None:
                    output_lines.append(parsed_output)

        # We also write the result to an output file (in case this is specified)
        if output_file is not None:

            # We open the output file for writing.
            with open(output_file, "w") as fp:

                # We write away each of the lines.
                for line in output_lines:
                    fp.write(line + "\n")

        # We return the output.
        return output_lines

    @staticmethod
    def parse_files(input_files, parse_function, output_files=None):

        # The results of parsing the file individually.
        results = []

        # We parse each file using the parse function and corresponding output file.
        for idx, input_file in enumerate(input_files):
            results.append(Parser.parse_file(input_file, parse_function,
                           output_files[idx] if output_files is not None else None))

        # We return the results.
        return results

def section_extracter(line):
    """
    Method used to extract the relevant function sections.
    :param line: the current line in the file.
    :return: a list of relevant function sections.
    """
    result = re.search('([^ ]*.text.[^ \n]*)', line)
    if result is not None:
        return result.group(0)
