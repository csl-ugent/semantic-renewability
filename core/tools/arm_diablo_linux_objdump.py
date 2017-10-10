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

    def compare_binaries(self, binaries):
        """
        Method used to compare all binaries.
        :param binaries: the binaries to compare.
        :return: True if the binaries are all the same, False if they are not.
        """

        # A function to clean disassembly lines so irrelevant information (that might differ
        # between versions however) is filtered out
        def clean(line):
            # Remove everything that comes after a semicolon
            semicolon = line.find(';')
            if semicolon != -1:
                line = line[:semicolon]

            # Remove everything between angular brackets
            lb = line.find('<')
            rb = line.find('>')
            if lb != -1 and rb != -1:
                line = line[:lb +1] + line[rb:]

            return line

        # Get all the contents in binary
        dumps = []
        for binary in binaries:
            output = subprocess.check_output([self.bin_location, '--full-contents', binary], universal_newlines=True)

            # Split into sections and dump the first element (only contains file name, which differs)
            sections = output.split('Contents of section ')[1:]
            for idx, sec in enumerate(sections):
                if sec.startswith('.text'):
                    # Get the name of the section, and obtain its disassembly
                    section_name = sec[:sec.find(':')]
                    output = subprocess.check_output([self.bin_location, '--disassemble', '--section=' + section_name, binary], universal_newlines=True)

                    # Filter the disassembly by removing the file name, the .word instructions,
                    # and cleaning the line
                    lines = output[output.find('Disassembly'):].splitlines()
                    lines = [clean(line) for line in lines if '.word' not in line]
                    sections[idx] = '\n'.join(lines)
                if sec.startswith('.dynsym'):
                    # The contents of this section can differ (function size). TODO: Actually interpret this data and simply compare the relevant parts.
                    sections[idx] = ''

            dumps.append(''.join(sections))

        # Compare the dumps
        return len(set(dumps)) <= 1

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
