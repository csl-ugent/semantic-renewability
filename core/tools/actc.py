import os
import subprocess

class ACTC:
    """
    Class which represents the ACTC toolchain.
    """
    def __init__(self, bin_location, config, path):
        """
        Method used to initialize this tool.
        :param bin_location: the location where the binary of this tool can be found.
        :param config: the ACTC config dictionary.
        :param path: the path where ACTC output is to go.
        :return: nothing.
        """
        self.bin_location = bin_location
        self.config = config
        self.path = path

    def clean(self, config_file):
        """
        Method used to clean previous executions of the actc tool.
        :param config_file: the absolute path to the config file that will be used by the ACTC
        :return: nothing.
        """
        # Execute the command.
        subprocess.check_call([self.bin_location, '-f', config_file, 'clean'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def execute(self, config_file):
        """
        Method used to execute the actc tool.
        :param config_file: the absolute path to the config file that will be used by the ACTC
        :return: nothing.
        """
        # Construct the ACTC command.
        command_exec = [self.bin_location, '--aidfixed', self.config['aid'], '-f', config_file, '-d', 'build']

        # Execute the command.
        subprocess.check_call(command_exec, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def get_build_dir(self, name):
        """
        Method used to get the path to the build directory.
        :param name: the name for the ACTC config.
        :return: path to the ACTC build directory.
        """

        return os.path.join(self.path, 'build', name)

    def get_mobile_blocks_dir(self, name):
        """
        Method used to get the path to the mobile blocks directory.
        :param name: the name for the ACTC config.
        :return: path to the ACTC mobile blocks directory.
        """

        return os.path.join(self.get_output_dir(name), 'mobile_blocks')

    def get_output_dir(self, name):
        """
        Method used to get the path to the ACTC output directory.
        :param name: the name for the ACTC config.
        :return: path to the ACTC output directory.
        """

        return os.path.join(self.get_build_dir(name), 'BC05')
