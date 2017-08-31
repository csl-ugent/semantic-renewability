import logging
import subprocess

class ARMDiabloLinuxObjdump:
    """
    Class which represents the diablo modified linux objdump tool.
    """
    def __init__(self, bin_location):
        """
        Method used to initialize this tool.
        :param bin_location: the location where the binary of this tool can be found.
        :return: nothing.
        """
        self.bin_location = bin_location

    def disassemble_obj_file(self, flags, object_file, output_file):
        """
        Method used to disassemble an object file.
        :param flags: the flags used for this disassembler.
        :param object_file: the object file which should be disassembled.
        :param output_file: the resulting output file name.
        :return: nothing.
        """
        # Debug
        logging.debug("Disassembling file: " + str(object_file) + " with flags: " + str(flags))

        # Construct the disassemble command.
        command_exec = [self.bin_location] + flags + [object_file]

        # Execute the disassembler.
        with open(output_file, 'w') as f_out:
            subprocess.check_call(command_exec, stdout=f_out)

    def disassemble_obj_files(self, flags, object_files, output_files):
        """
        Method used to disassemble multiple object files at once.
        :param flags: the flags used for this disassembler.
        :param object_files: the object files which should be disassembled.
        :param output_files: the resulting output file name.
        :return nothing.
        """
        # Debug
        logging.debug("Disassembling files: " + str(object_files) + " with flags: " + str(flags))

        # Disassemble each file individually.
        for idx, object_file in enumerate(object_files):
            self.disassemble_obj_file(flags, object_file, output_files[idx])
