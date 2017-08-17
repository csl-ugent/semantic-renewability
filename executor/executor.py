import os
import logging
import shutil
import configparser
import json

import core.file as file
import core.parser as parser
import core.func_sections as func_sections
import core.templates as templates
import core.script as script
import core.rethinkdb as rethinkdb

import core.tools.semantic_mod as semantic_mod
import core.tools.arm_diablo_linux_gcc as arm_diablo_linux_gcc
import core.tools.arm_diablo_linux_objdump as arm_diablo_linux_objdump
import core.tools.elf_reader as elf_reader
import core.tools.actc as actc
import core.tools.util as util


class Executor:
    """
    Class responsible for execution the whole semantic renewability on
    a high level.
    """

    def __init__(self, config):
        """
        Initialization of the executor.
        :param config: the parsed configuration file (see config.py)
        :return: nothing.
        """
        self.config = config

    def execute_directory_pre(self):
        """
        Method which executes the pre execution steps towards
        the output directory.
        :return: tuple of the input directory structure and list of source files in the input directory.
        """
        # The first step is analyzing the source input directory.
        directory_structure_input = file.discover_full_file_hierarchy(self.config.default['input_source_directory'],
                                                                [self.config.default['suffix_source'],
                                                                 self.config.default['suffix_header']])
        logging.debug("Directory structure: " + str(directory_structure_input))

        # We extract the source files out of the directory structure.
        source_files = file.filter_directory_structure(directory_structure_input,
                                                       [self.config.default['suffix_source']])

        # We make sure the output directory is empty.
        try:
            shutil.rmtree(self.config.default['output_directory'])
        except FileNotFoundError:
            # We can safely ignore the file not found error: the directory simply does not exist yet
            # and should be created by the 'semantic_mod' tool.
            pass

        # Return a tuple of generated relevant information.
        return directory_structure_input, source_files

    def execute_semantic_mod(self, directory_structure_input, source_files, mode):
        """
        Method which applies the semantic modification tool for source to source transformations.
        :param directory_structure_input: the input directory structure.
        :param source_files: list of source files in the input directory.
        :param mode: the type of transformation to apply.
        :return: a list of generated versions in the output directory.
        """
        # We execute the semantic modification tool with the given source files (and options).
        logging.debug("Starting the struct reordering source to source transformations...")
        semantic_mod_tool = semantic_mod.SemanticMod(self.config.semantic_mod['bin_location'],
                                                     self.config.semantic_mod['compiler_flags'])
        extra_opts = []
        if mode == "StructReordering":
            extra_opts = ['-sr_am', str(self.config.struct_reordering['amount'])]
        elif mode == "FPReordering":
            extra_opts = ['-fp_am', str(self.config.functionparam_reordering['amount'])]

        semantic_mod_tool.execute_structure_reordering(self.config.default['input_source_directory'], source_files,
                                                       self.config.default['output_directory'],
                                                       mode,
                                                       extra_opts)

        # We analyze the output directory.
        generated_versions = file.discover_subdirectories(self.config.default['output_directory'])
        logging.debug("Versions: " + str(generated_versions))
        logging.debug("Tool generated: " + str(len(generated_versions)) + " out of " +
                      self.config.struct_reordering['amount'] + " requested versions.")

        # We iterate over each generated version.
        for version in generated_versions:

            # We obtain the directory structure of the given version.
            version_directory = os.path.join(self.config.default['output_directory'], version)
            directory_structure_version = file.discover_full_file_hierarchy(version_directory,
                                                                            [self.config.default['suffix_source'],
                                                                             self.config.default['suffix_header']])

            # We copy all files that were not modified (aka not available in the modified directory) to the
            # modified directory in order to obtain full source directories.
            file.copy_files_from_directory_to_directory_structure(directory_structure_input,
                                                                  self.config.default['input_source_directory'],
                                                                  directory_structure_version,
                                                                  version_directory)

        # We return a list of generated versions in the output directory.
        return generated_versions

    def execute(self):
        """
        Method used to start the execution of the main flow.
        :return: nothing.
        """

        # We apply pre execution steps towards the output directory.
        (directory_structure_input, source_files) = self.execute_directory_pre()

        # We apply the semantic modification tool for source to source transformations.
        generated_versions = self.execute_semantic_mod(directory_structure_input, source_files,
                                                       self.config.semantic_mod['type'])

        # We create an instantiation of the ARM diablo linux gcc.
        compiler = arm_diablo_linux_gcc.ARMDiabloLinuxGCC(self.config.arm_diablo_linux_gcc['bin_location'])

        # We create an instantiation of the ARM diablo linux objdump.
        objdump = arm_diablo_linux_objdump.ARMDiabloLinuxObjdump(self.config.arm_diablo_linux_objdump['bin_location'])

        # We create an instantiation of the ELF reader tool.
        elf_reader_ = elf_reader.ElfReader(self.config.elf_reader['bin_location'])

        # We create an instantiation of the ACTC tool chain.
        actc_ = actc.ACTC(self.config.actc['bin_location'])

        # We create an instantiation of the rethinkdb.
        rethinkdb_ = rethinkdb.RethinkDB(self.config.rethinkdb['host'],
                                         self.config.rethinkdb['port'],
                                         self.config.rethinkdb['database'])

        # We set up the testing environment.
        testing_directory = os.path.join(self.config.default['output_directory'], 'testing')
        os.makedirs(os.path.join(testing_directory), exist_ok=True)

        # We create a new entry in the 'experiments' table of the rethinkdb.
        experiment_id = rethinkdb_.add_experiment(self.config.rethinkdb['table_experiments'])
        logging.debug("Experiment id: " + experiment_id)

        # We create a dictionary with important analytics information.
        analytics = dict()
        analytics['general'] = dict()
        analytics['functions'] = dict()

        # We add some analytics information.
        analytics['general']['source_files'] = len(source_files)
        analytics['general']['source_input'] = self.config.default['input_source_directory']
        analytics['general']['transformations'] = len(generated_versions)

        # We build a dictionary containing all relevant information of the current version.
        version_information = dict()
        for version in generated_versions:

            # Create dictionary for this specific version.
            version_information[version] = dict()

            # The location of the generated source files of this version.
            version_information[version]["version_directory"] = os.path.join(self.config.default['output_directory'],
                                                                             version)

            # The location that will be used for version related analysis.
            version_information[version]["analysis_directory"] = os.path.join(self.config.default['output_directory'],
                                                                              version + "_analysis")

            # The directory within the analysis directory that will be used to store compiled source files.
            version_information[version]["object_files_directory"] = os.path.join(
                                                                    version_information[version]["analysis_directory"],
                                                                    "objfiles")

            # The directory structure of the version source and header files.
            version_information[version]["directory_structure"] = file.discover_full_file_hierarchy(
                                                                    version_information[version]["version_directory"],
                                                                    [self.config.default['suffix_source'],
                                                                     self.config.default['suffix_header']])

            # List of absolute paths to source files of this specific version.
            version_information[version]["source_files"] = file.filter_directory_structure(
                                                            version_information[version]["directory_structure"],
                                                            [self.config.default['suffix_source']])

            # List of absolute paths to the object files in the object files directory.
            version_information[version]["object_files"] = file.create_output_paths(
                                                                version_information[version]["source_files"],
                                                                version_information[version]["version_directory"],
                                                                version_information[version]["object_files_directory"],
                                                                ".o")

            # List of absolute paths to the disassembled files in the object files directory.
            version_information[version]["diss_files"] = file.create_output_paths(
                                                                version_information[version]["source_files"],
                                                                version_information[version]["version_directory"],
                                                                version_information[version]["object_files_directory"],
                                                                "_diss.out")

            # List of absolute paths to ELF files in the object files directory.
            version_information[version]["elf_files"] = file.create_output_paths(
                                                                version_information[version]["source_files"],
                                                                version_information[version]["version_directory"],
                                                                version_information[version]["object_files_directory"],
                                                                ".elf")

            # List of absolute paths to section files in the object files directory.
            version_information[version]["section_files"] = file.create_output_paths(
                                                                version_information[version]["source_files"],
                                                                version_information[version]["version_directory"],
                                                                version_information[version]["object_files_directory"],
                                                                ".sections")

            # We read the generated transformation.json file and add the information to the rethinkdb.
            transformation_id = rethinkdb_.add_transformation(self.config.rethinkdb['table_transformations'],
                                                              experiment_id,
                                                              version,
                                                              file.read_json(os.path.join(version_information[version]
                                                                                          ["version_directory"],
                                                                             'transformations.json')))
            logging.debug("Transformation id: " + transformation_id)

            # The first step is to compile all source files into object files in the analysis directory
            compiler.create_object_files(self.config.arm_diablo_linux_gcc["base_flags"],
                                         version_information[version]["source_files"],
                                         version_information[version]["object_files"])

            # We disassemble the generated object files (for DEBUGGING purposes ONLY!)
            objdump.disassemble_obj_files(self.config.arm_diablo_linux_objdump["base_flags"],
                                          version_information[version]["object_files"],
                                          version_information[version]["diss_files"])

            # We dump all relevant section information using readelf.
            elf_reader_.read_files(self.config.elf_reader["base_flags"],
                                   version_information[version]["object_files"],
                                   version_information[version]["elf_files"])

            # We use a custom parser to parse all relevant code (.text) sections
            # out of the ELF files.
            # result is a list of a list of section names.
            # every list in result corresponds to a parsed input file.
            result = parser.Parser.parse_files(version_information[version]["elf_files"],
                                               parser.section_extracter,
                                               version_information[version]["section_files"])

            # We iterate over sets of sections.
            # We are going to store information regarding the different sections in a dictionary.
            # {obj_file_name: (obj_path, {func_name: [sections]})}
            version_information[version]["section_information"] = dict()
            for idx, sect in enumerate(result):

                    # We obtain the relative path to the file of the corresponding object file.
                    obj_file_name = file.obtain_rel_path(version_information[version]["object_files"][idx],
                                                         version_information[version]["object_files_directory"])

                    # We create an entry base on the relative path and add a tuple of the full path
                    # and an empty dictionary.
                    version_information[version]["section_information"][obj_file_name] = \
                        (version_information[version]["object_files"][idx], dict())

                    # We iterate over all sections.
                    for section in sect:

                        # We determine the function to which it corresponds.
                        function_name = util.extract_function_name_from_section(section)

                        # We check if the function already exists in our dictionary.
                        if function_name not in version_information[version]["section_information"][obj_file_name][1]:

                            # We create a new entry containing a single list with the section.
                            version_information[version]["section_information"][obj_file_name][1][function_name] = \
                                [section]
                        else:
                            # We add the section to the existing list.
                            version_information[version]["section_information"][obj_file_name][1][function_name].\
                                append(section)

            # Debug information.
            logging.debug("Section information for version: " + version +
                          " is: " + str(version_information[version]["section_information"]))

        # We will compare the section information of all version and decide which functions need to
        # made mobile.
        analytics['general']['amount_functions'] = 0

        # The functions which are considered 'different'.
        functions_diff = set()

        # The sections of functions which are different.
        functions_sections_diff = dict()

        # We will start comparing the sections of the different versions.
        for i in range(len(generated_versions)-1):

            # The name of the first and second version.
            version_one = generated_versions[i]
            version_two = generated_versions[i+1]

            # Debug.
            logging.debug("Comparing version: " + version_one + " and version: " + version_two)

            # Iterate over all object files (we assume both versions have the same object files).
            for object_file in version_information[version]["section_information"]:

                # We obtain the path to the version specific object file.
                path_obj_file_version_one = version_information[version_one]["section_information"][object_file][0]
                path_obj_file_version_two = version_information[version_two]["section_information"][object_file][0]

                # Iterate over all functions within this object file.
                # (we assume both versions have the same functions)
                for function in version_information[version_one]["section_information"][object_file][1].keys():

                    # Increase amount of functions.
                    if i == 0:
                        analytics['general']['amount_functions'] += 1
                        analytics['functions'][function] = dict()
                        analytics['functions'][function]['reasons'] = []

                    # We create an entry in the function section difference dictionary.
                    functions_sections_diff[function] = []

                    # If the amount of sections of a function differs, they are considered different.
                    if len(version_information[version_one]["section_information"][object_file][1][function]) != \
                            len(version_information[version_two]["section_information"][object_file][1][function]):

                        # Debug.
                        logging.debug("Function: " + function +
                                      " has different amount of sections in both versions, version one: " +
                                      str(version_information[version_one]["section_information"][object_file][1]
                                          [function]) +
                                      " version two: " +
                                      str(version_information[version_two]["section_information"][object_file][1]
                                          [function]))

                        # We add information to our analytics.
                        analytics['functions'][function]['reasons'].append("Different amount of sections comparing " +
                                                                           "version: \n" + version_one + "(" +
                                                                           str(version_information[version_one]
                                                                                ["section_information"][object_file][1]
                                                                                [function]) + ")\nand version: " +
                                                                           version_two + "(" +
                                                                           str(version_information[version_two]
                                                                               ["section_information"][object_file][1]
                                                                               [function]) + ").\n\n")

                        # We append the function to the list of functions which are considered different.
                        functions_diff.add((function, object_file))
                        continue

                    # If the amount of sections are equal, we can start comparing the functions.
                    for section in version_information[version_one]["section_information"][object_file][1][function]:

                        # We compare the specific section using the version one and version two object file.
                        if not func_sections.compare_sections(elf_reader_, section, section, path_obj_file_version_one,
                                                              path_obj_file_version_two):

                            # If the sections are not equal, the functions are considered different.
                            functions_diff.add((function, object_file))

                            # We keep track of the specific function that is different.
                            functions_sections_diff[function].append(section)

                            # We add information to our analytics.
                            analytics['functions'][function]['reasons'].append("Section: " + section +
                                                                               " is different when comparing\n" +
                                                                               "version: " + version_one +
                                                                               " and version: " +
                                                                               version_two + ".\n\n")

                            # Debug.
                            logging.debug("Section: " + section + " is different when comparing version: " +
                                          version_one + " and version: " + version_two)

        # We determine which functions remained the same.
        functions_equal = set()
        if len(generated_versions) > 0:

            # We take the first version and iterate over all object files.
            version = generated_versions[0]
            for object_file in version_information[version]["section_information"]:

                # Iterate over all functions within this object file.
                for function in version_information[version_one]["section_information"][object_file][1].keys():

                    # If the function was not different, we add it to the set of equal functions.
                    if (function, object_file) not in functions_diff:
                        functions_equal.add((function, object_file))

        # Store all analytics information with respect to the mobile functions/fixed functions.
        analytics['general']['mobile_functions'] = []
        for idx, (function, obj_file) in enumerate(functions_diff):
            analytics['general']['mobile_functions'].append({'name': function, 'object_file': obj_file})
            analytics['functions'][function]['mobile'] = True
            analytics['functions'][function]['obj_file'] = obj_file
        analytics['general']['amount_mobile'] = len(analytics['general']['mobile_functions'])

        analytics['general']['fixed_functions'] = []
        for idx, (function, obj_file) in enumerate(functions_equal):
            analytics['general']['fixed_functions'].append({'name': function, 'object_file': obj_file})
            analytics['functions'][function]['mobile'] = False
            analytics['functions'][function]['obj_file'] = obj_file

        # Transformation of analytics (convenience)
        function_data = []
        for function in analytics['functions'].keys():
            function_data.append({'name': function, 'mobile': analytics['functions'][function]['mobile'],
                                  'reasons': analytics['functions'][function]['reasons'],
                                  'obj_file': analytics['functions'][function]['obj_file']})

        analytics['functions'] = function_data

        # Debug
        logging.debug("Functions considered different: " + str(functions_diff))
        logging.debug("Sections which are different: " + str(functions_sections_diff))

        # Store the analytics information into the rethinkdb.
        rethinkdb_.add_analytics(self.config.rethinkdb['table_analytics'], experiment_id, analytics)

        # If in testmode we will stop execution here
        # and output the result as a json file as well.
        if self.config.default["testmode"] is True:

            # Construct file name path.
            filename = ""
            if self.config.semantic_mod["type"] == "StructReordering":
                filename = os.path.join(self.config.default['testmodedirectory'],
                                        "struct_reordering_" + str(self.config.struct_reordering["amount"]))
            elif self.config.semantic_mod["type"] == "FPReordering":
                filename = os.path.join(self.config.default['testmodedirectory'],
                                        "function_param_reordering_" +
                                        str(self.config.functionparam_reordering["amount"]))
            with open(filename + ".json", 'w') as f:
                data = dict()
                data["amount_functions"] = analytics["general"]["amount_functions"]
                data["amount_mobile"] = analytics["general"]["amount_mobile"]
                json.dump(data, f, ensure_ascii=False)
            return

        # The directory in which annotations will be stored.
        annotations_path = os.path.join(self.config.default['output_directory'], 'actc',
                                        "annotations.out")

        # We generate annotations for the functions which have to be made mobile (using a predefined template).
        logging.debug("Creating mobile block annotations...")
        annotations = []
        for (func, object_file) in functions_diff:

            # Function specific annotation.
            annotations.append(templates.read_template_and_fill('function_annotation.template', {'function': func},
                                                                None))

        # Write the annotation away in comma-separated style.
        templates.read_template_and_fill('annotations.template', {'functions': ','.join(annotations)},
                                         annotations_path)

        # We will generate ACTC config files for each of the generated versions.
        for version in generated_versions:

            actc_path = os.path.join(self.config.default['output_directory'], 'actc', 'aspire_' + version + '.json')
            version_information[version]["actc_config"] = actc_path

            # We need to convert our directory structure to a list of source and header files.
            src_header_files = file.filter_directory_structure(version_information[version]["directory_structure"],
                                                               [self.config.default['suffix_source'],
                                                                self.config.default['suffix_header']])

            # We write the list to a specified format required by the ACTC config file.
            src_header_files_input = ', '.join(["\"" + x + "\"" for x in src_header_files])

            # ACTC configuration file generation (based on a predefined template).
            templates.read_template_and_fill('actc_config.template',
                                             {'source_code': src_header_files_input,
                                              'annotations': annotations_path},
                                             actc_path)

            # Now we will employ the ACTC using our mobile block annotations and actc configuration file.
            actc_.execute(self.config.actc['base_flags'], actc_path, 'clean')
            if actc_.execute(self.config.actc['base_flags'], actc_path, 'build') != 0:
                logging.debug("ACTC didn't work... retrying one time...")
                actc_.execute(self.config.actc['base_flags'], actc_path, 'build')

        # First we clear arndale testing directory.
        script.execute_scripts("arndale_clear.sh", ["arndale_external"])

        # We transfer the testing framework and config file.
        script.execute_scripts("transfer_arndale_testing_framework.sh",
                               [os.path.abspath(os.path.join('transferable', 'testing', 'test.py')),
                                self.config.testing['input_output'],
                                "arndale_external"])

        # We will now try to deploy all of the versions and corresponding mobile blocks to arndale.
        for version_one in generated_versions:
            for version_two in generated_versions:

                # We generate the paths for both the first and the second version.
                version_one_path = os.path.join(self.config.default['output_directory'],
                                                'actc', 'build', 'aspire_' + version_one)
                version_two_path = os.path.join(self.config.default['output_directory'],
                                                'actc', 'build', 'aspire_' + version_two)

                # Construct the version name.
                version_name = 'E_' + version_one + '_M_' + version_two

                # We execute a script to transfer the generated files to arndale.
                script.execute_scripts("transfer_arndale_version.sh",
                                       [version_one_path, version_two_path,
                                        version_name,
                                        "arndale_external"])

                # We test the generated version on arndale.
                script.execute_scripts("transfer_arndale_testing_version.sh",
                                       [version_name, testing_directory,
                                        "arndale_external"])

                # We add test related data to the rethinkdb.
                test_id = rethinkdb_.add_test(self.config.rethinkdb['table_tests'],
                                              experiment_id,
                                              version_one,
                                              version_two,
                                              file.read_json(os.path.join(testing_directory, version_name + ".json")))
                logging.debug("Test id: " + test_id)

