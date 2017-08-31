import subprocess

class SemanticMod:
    """
    Class which represents the Semantic Modification libtooling stand-alone tool.
    This tool is used to perform source to source transformations using the LLVM compiler driver.
    """
    def __init__(self, bin_location, compiler_flags):
        """
        Method used to initialize this tool.
        :param bin_location: the location where the binary of this tool can be found.
        :return: nothing.
        """
        self.bin_location = bin_location
        self.compiler_flags = compiler_flags

    def execute_structure_reordering(self, base_directory, source_files, output_directory, mode, extra_opts):
        """
        Method used to perform the source to source transformation for structure field reordering.
        :param base_directory: the root directory of the source files.
        :param source_files: a list of input source files to be (potentially) transformed.
        :param output_directory: the location in which the transformed source files will be put.
        :param mode: the type of transformation to be applied.
        :param extra_opts: some extra options for this specific transformation.
        :return: nothing.
        """

        # We build the command to be executed.
        command_exec = [self.bin_location] + source_files + ['-transtype', mode] + ['-bd', base_directory] + \
                       ['-od', output_directory] + extra_opts + ["--"] + self.compiler_flags

        # We execute the command.
        subprocess.check_call(command_exec)
