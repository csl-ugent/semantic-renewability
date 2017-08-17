import logging

import core.command as cmd
import core.tools.util as util


class ARMDiabloLinuxGCC:
    """
    Class which represents the diablo modified linux gcc compiler.
    """
    def __init__(self, bin_location):
        """
        Method used to initialize this tool.
        :param bin_location: the location where the binary of this tool can be found.
        :return: nothing.
        """
        self.bin_location = bin_location

    def create_object_file(self, flags, source_file, output_file=None):
        """
        Method used to compile a single source file to an object file.
        :param flags: string of flags which should be used.
        :param source_file: path to the source file.
        :return: nothing.
        """
        # Debug information.
        logging.debug("Creating object file for: " + str(source_file) + " with flags: " + str(flags))

        # We build the command to be executed.
        command_exec = [self.bin_location, '-c'] + (['-o', output_file] if output_file is not None else []) +\
            flags + [source_file]

        # We execute the command.
        (status, stdout, stderr) = cmd.execute_command_status_output(command_exec)
        util.handle_status(status, stdout, stderr)

    def create_object_files(self, flags, source_files, output_files=None):
        """
        Method used to compile multiple source files to object files.
        :param source_files: list of paths to the source files.
        :param flags: string of flags which should be used.
        :return: nothing.
        """
        # Debug information.
        logging.debug("Creating object files for: " + str(source_files) + " with flags: " + str(flags))

        # We will convert each given source file to an object file.
        for idx, file in enumerate(source_files):
            self.create_object_file(flags, file, output_files[idx] if output_files is not None else None)