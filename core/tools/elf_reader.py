import logging
import subprocess

class ElfReader:
    """
    Class which represents an ELF file format reader.
    """
    def __init__(self, bin_location):
        """
        Method used to initialize this tool.
        :param bin_location: the location where the binary of this tool can be found.
        :return: nothing.
        """
        self.bin_location = bin_location

    def read_file(self, flags, object_file, output_file=None):
        """
        Method used to read the ELF file format with given flags.
        :param flags: the flags used by the ELF reader.
        :param object_file: the input of the ELF reader.
        :param output_file: the output file name of the ELF reader.
        :return: status, stdout and stderr.
        """
        # Debug
        logging.debug("Reading ELF file format of : " + str(object_file) + " with flags: " + str(flags))

        # Construct the disassemble command.
        command_exec = [self.bin_location] + flags + [object_file]

        # Execute the disassembler.
        if output_file:
            with open(output_file, 'w') as f_out:
                subprocess.check_call(command_exec, stdout=f_out)
        else:
            return subprocess.check_output(command_exec)

    def read_files(self, flags, object_files, output_files):
        """
        Method used to read multiple ELF file formats with given flags.
        :param flags: the flags used by the ELF reader.
        :param object_files: the inputs of the ELF reader.
        :param output_files: the output file names of the ELF reader.
        :return: nothing.
        """
        # Debug
        logging.debug("Reading ELF files: " + str(object_files) + " with flags: " + str(flags))

        # Disassemble each file individually.
        for idx, object_file in enumerate(object_files):
            self.read_file(flags, object_file, output_files[idx])
