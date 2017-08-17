import core.command as cmd
import core.tools.util as util


class ACTC:
    """
    Class which represents the ACTC toolchain.
    """
    def __init__(self, bin_location):
        """
        Method used to initialize this tool.
        :param bin_location: the location where the binary of this tool can be found.
        :return: nothing.
        """
        self.bin_location = bin_location

    def execute(self, flags, config_file, mode):
        """
        Method used to execute the actc tool.
        :param flags: the flags which will be passed to the ACTC.
        :param config_file: the absolute path to the config file that will be used by the ACTC
        :param mode: the mode of ACTC (e.g. 'build' or 'clean').
        :return: status of the tool.
        """
        # Construct the ACTC command.
        command_exec = [self.bin_location] + flags + ["-f", config_file, "-d", mode]

        # Execute the command.
        (status, stdout, stderr) = cmd.execute_command_status_output(command_exec)

        # We return the status.
        return status
