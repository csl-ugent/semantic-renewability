import json
import logging


class Config:
    """
    Class containing all relevant information related to the config file (config.ini).
    """

    def __init__(self, config_file):

        # We define the relevant instance attributes.
        self.default = dict()
        self.rethinkdb = dict()
        self.testing = dict()
        self.semantic_mod = dict()
        self.arm_diablo_linux_gcc = dict()
        self.arm_diablo_linux_objdump = dict()
        self.elf_reader = dict()
        self.actc = dict()

        # We parse the given config file.
        self.parse_config(config_file)

    def parse_config(self, config_file):
        """
        Method used to parse the given config file.
        We keep all relevant information within this object instance for later use.
        :param config_file: the config file (configparser.py)
        :return: nothing.
        """

        # Parsing the DEFAULT section.
        logging.debug("Parsing the DEFAULT section...")
        self.default['binary_name'] = config_file.get("DEFAULT", "BinaryName")
        self.default['input_source_directory'] = config_file.get("DEFAULT", "InputSourceDirectory")
        self.default['output_directory'] = config_file.get("DEFAULT", "OutputDirectory")
        self.default['suffix_source'] = config_file.get("DEFAULT", "SuffixSource")
        self.default['suffix_header'] = config_file.get("DEFAULT", "SuffixHeader")
        self.default['nr_of_versions'] = config_file.get("DEFAULT", "NrOfVersions")

        # Parsing the RETHINKDB section.
        logging.debug("Parsing the RETHINKDB section...")
        self.rethinkdb['host'] = config_file.get("RETHINKDB", "Host")
        self.rethinkdb['port'] = config_file.get("RETHINKDB", "Port")
        self.rethinkdb['database'] = config_file.get("RETHINKDB", "Database")
        self.rethinkdb['table_experiments'] = config_file.get("RETHINKDB", "TableExperiments")
        self.rethinkdb['table_analytics'] = config_file.get("RETHINKDB", "TableAnalytics")
        self.rethinkdb['table_transformations'] = config_file.get("RETHINKDB", "TableTransformations")
        self.rethinkdb['table_tests'] = config_file.get("RETHINKDB", "TableTests")

        # Parsing the TESTING section.
        logging.debug("Parsing the TESTING section...")
        self.testing['input_output'] = config_file.get("TESTING", "InputOutput")
        self.testing['host'] = config_file.get("TESTING", "Host")
        self.testing['regression_dir'] = config_file.get("TESTING", "RegressionDir")

        # Parsing the SEMANTIC_MOD section.
        logging.debug("Parsing the SEMANTIC_MOD section...")
        self.semantic_mod['bin_location'] = config_file.get("SEMANTIC_MOD", "BinLocation")
        self.semantic_mod['seed'] = config_file.get("SEMANTIC_MOD", "Seed")
        self.semantic_mod['type'] = config_file.get("SEMANTIC_MOD", "Type")

        # Parsing the ARM_DIABLO_LINUX_GCC section.
        logging.debug("Parsing the ARM_DIABLO_LINUX_GCC section...")
        self.arm_diablo_linux_gcc["bin_location"] = config_file.get("ARM_DIABLO_LINUX_GCC", "BinLocation")

        # Parsing the ARM_DIABLO_LINUX_OBJDUMP section.
        logging.debug("Parsing the ARM_DIABLO_LINUX_OBJDUMP section...")
        self.arm_diablo_linux_objdump["bin_location"] = config_file.get("ARM_DIABLO_LINUX_OBJDUMP", "BinLocation")
        self.arm_diablo_linux_objdump["base_flags"] = json.loads(config_file.get("ARM_DIABLO_LINUX_OBJDUMP", "BaseFlags"))

        # Parsing the ELF_READER section.
        logging.debug("Parsing the ELF_READER section...")
        self.elf_reader["bin_location"] = config_file.get("ELF_READER", "BinLocation")
        self.elf_reader["base_flags"] = json.loads(config_file.get("ELF_READER", "BaseFlags"))

        # Parsing the ACTC section.
        logging.debug("Parsing the ACTC section...")
        self.actc["aid"] = config_file.get("ACTC", "AID")
        self.actc["bin_location"] = config_file.get("ACTC", "BinLocation")
        self.actc["common_options"] = json.loads(config_file.get("ACTC", "CommonOptions"))
        self.actc["compiler_flags"] = json.loads(config_file.get("ACTC", "CompilerFlags"))
        self.actc["deploy_mobility_script"] = config_file.get("ACTC", "DeployMobilityScript")
        self.actc["linker_flags"] = json.loads(config_file.get("ACTC", "LinkerFlags"))
        self.actc["preprocessor_flags"] = json.loads(config_file.get("ACTC", "PreprocessorFlags"))
        self.actc["server"] = config_file.get("ACTC", "Server")
