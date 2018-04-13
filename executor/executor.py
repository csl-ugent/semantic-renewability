import json
import logging
import os
import subprocess

import core.file as file
import core.parser as parser
import core.sections as sections
import core.spec as spec
import core.templates as templates

import core.tools.actc as actc
import core.tools.arm_diablo_linux_gcc as arm_diablo_linux_gcc
import core.tools.arm_diablo_linux_objdump as arm_diablo_linux_objdump
import core.tools.elf_reader as elf_reader
import core.tools.semantic_mod as semantic_mod

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

        # We create an instantiation of the ARM diablo linux gcc.
        self.compiler = arm_diablo_linux_gcc.ARMDiabloLinuxGCC(self.config.arm_diablo_linux_gcc['bin_location'])

        # We create an instantiation of the ARM diablo linux objdump.
        self.objdump = arm_diablo_linux_objdump.ARMDiabloLinuxObjdump(self.config.arm_diablo_linux_objdump['bin_location'])

        # We create an instantiation of the ELF reader tool.
        self.elf_reader = elf_reader.ElfReader(self.config.elf_reader['bin_location'])

        # We create an instantiation of the ACTC tool chain.
        actc_path = os.path.join(self.config.default['output_directory'], 'actc')
        self.actc_ = actc.ACTC(self.config.actc['bin_location'], self.config.actc, actc_path)

    def analyze(self, source_files, generated_versions, version_information):
        # We create a dictionary with important analytics information.
        analytics = dict()
        analytics['general'] = dict()
        analytics['general']['source_files'] = len(source_files)
        analytics['general']['source_input'] = self.config.default['input_source_directory']
        analytics['general']['transformations'] = len(generated_versions)

        def analyze_symbols_in_section_info(generated_versions, version_information, section_info):
            # Initialize the symbol datastructures
            symbol_info = dict()
            for obj_name, obj in version_information[generated_versions[0]][section_info].items():
                for symbol in obj[1].keys():
                    symbol_tuple = (symbol, obj_name)
                    symbol_info[symbol_tuple] = dict()
                    symbol_info[symbol_tuple]['reasons'] = []

            # We will start comparing the sections of the different versions.
            symbols_diff = set()# The symbols which are considered 'different'.
            sections_diff = []# The sections that are different.
            for version_one, version_two in zip(generated_versions[:-1], generated_versions[1:]):
                logging.debug("Comparing version: " + version_one + " and version: " + version_two)

                # Iterate over all object files (we assume both versions have the same object files).
                for object_file in version_information[version_one][section_info]:
                    obj_dict_1 = version_information[version_one][section_info][object_file]
                    obj_dict_2 = version_information[version_two][section_info][object_file]

                    # Iterate over all symbols within this object file.
                    # (we assume both versions have the same symbols)
                    for symbol in obj_dict_1[1].keys():
                        symbol_tuple = (symbol, object_file)

                        # If the amount of sections for a symbol differ, they are considered different.
                        if len(obj_dict_1[1][symbol]) != len(obj_dict_2[1][symbol]):
                            # Debug.
                            logging.debug("Symbol: " + symbol + " has different amount of sections in both versions, version one: " +
                                    str(obj_dict_1[1][symbol]) + " version two: " + str(obj_dict_2[1][symbol]))

                            # We add information to our analytics.
                            symbol_info[symbol_tuple]['reasons'].append("Different amount of sections comparing " + "version: \n" + version_one +
                                    "(" + str(obj_dict_1[1][symbol]) + ")\nand version: " + version_two + "(" + str(obj_dict_2[1][symbol]) + ").\n\n")

                            # We append the symbol to the list of symbols which are considered different.
                            symbols_diff.add(symbol_tuple)
                            continue

                        # If the amount of sections are equal, we can start comparing the symbols.
                        for section in obj_dict_1[1][symbol]:
                            # We compare the specific section using the version one and version two object file.
                            if not sections.compare(self.elf_reader, section, section, obj_dict_1[0], obj_dict_2[0]):
                                # If the sections are not equal, the symbols are considered different.
                                symbols_diff.add(symbol_tuple)

                                # We keep track of the specific symbol that is different.
                                sections_diff.append((object_file, symbol, section))

                                # We add information to our analytics.
                                symbol_info[symbol_tuple]['reasons'].append("Section: " + section + " is different when comparing\n" +
                                        "version: " + version_one + " and version: " + version_two + ".\n\n")

                                # Debug.
                                logging.debug("Section: " + section + " is different when comparing version: " + version_one + " and version: " + version_two)

            return (symbol_info, symbols_diff, sections_diff)

        analytics['functions'], functions_diff, sections_diff = analyze_symbols_in_section_info(generated_versions, version_information, "text_section_information")
        analytics['general']['amount_functions'] = len(analytics['functions'])
        _, data_diff, data_sections_diff = analyze_symbols_in_section_info(generated_versions, version_information, "data_section_information")
        sections_diff = sections_diff + data_sections_diff

        # We determine which functions remained the same.
        functions_equal = set()
        if len(generated_versions):
            # We take the first version and iterate over all object files.
            version = generated_versions[0]
            for object_file in version_information[version]["text_section_information"]:
                for function in version_information[version]["text_section_information"][object_file][1].keys():
                    # If the function was not different, we add it to the set of equal functions.
                    if (function, object_file) not in functions_diff:
                        functions_equal.add((function, object_file))

        # Store all analytics information with respect to the mobile functions/fixed functions.
        analytics['general']['mobile_functions'] = []
        for idx, (function, object_file) in enumerate(functions_diff):
            function_tuple = (function, object_file)
            analytics['general']['mobile_functions'].append({'name': function, 'object_file': object_file})
            analytics['functions'][function_tuple]['mobile'] = True
            analytics['functions'][function_tuple]['obj_file'] = object_file
        analytics['general']['amount_mobile'] = len(analytics['general']['mobile_functions'])

        analytics['general']['fixed_functions'] = []
        for idx, (function, object_file) in enumerate(functions_equal):
            function_tuple = (function, object_file)
            analytics['general']['fixed_functions'].append({'name': function, 'object_file': object_file})
            analytics['functions'][function_tuple]['mobile'] = False
            analytics['functions'][function_tuple]['obj_file'] = object_file

        # Transformation of analytics (convenience)
        function_data = []
        for (function, object_file) in analytics['functions'].keys():
            function_tuple = (function, object_file)
            function_data.append({'name': function, 'mobile': analytics['functions'][function_tuple]['mobile'],
                                  'reasons': analytics['functions'][function_tuple]['reasons'],
                                  'obj_file': object_file})

        analytics['functions'] = function_data

        # Transform the set of differing function tuples to a list of function names. There is a loss
        # of accuracy here, as the object file the function is actually from is discarded. This reflects
        # how annotations in Diablo will also simply match on function name, and not take the originating
        # object file into account.
        functions_diff = list(functions_diff)
        functions_diff = [function for (function, object_file) in functions_diff]

        # Debug
        logging.debug("Functions considered different: " + str(functions_diff))
        logging.debug("Data considered different: " + str(data_diff))
        logging.debug("Sections which are different: " + str(sections_diff))

        return (analytics, functions_diff, data_diff)

    def execute_semantic_mod(self, source_files, mode):
        """
        Method which applies the semantic modification tool for source to source transformations.
        :param source_files: list of source files in the input directory.
        :param mode: the type of transformation to apply.
        :return: a list of generated versions in the output directory.
        """
        # We execute the semantic modification tool with the given source files (and options).
        logging.debug("Starting the struct reordering source to source transformations...")
        semantic_mod_tool = semantic_mod.SemanticMod(self.config.semantic_mod['bin_location'],
                                                     self.config.actc['preprocessor_flags'] + self.config.actc['common_options'])
        extra_opts = ['--nr_of_versions', str(self.config.default['nr_of_versions']), '--seed', self.config.semantic_mod['seed']]

        semantic_mod_tool.execute_structure_reordering(self.config.default['input_source_directory'], source_files,
                                                       self.config.default['output_directory'],
                                                       mode,
                                                       extra_opts)

        # We analyze the output directory.
        generated_versions = file.discover_subdirectories(self.config.default['output_directory'])
        logging.debug("Versions: " + str(generated_versions))
        logging.debug("Tool generated: " + str(len(generated_versions)) + " out of " +
                      self.config.default['nr_of_versions'] + " requested versions.")

        # We iterate over each generated version.
        for version in generated_versions:
            # We obtain the directory structure of the given version.
            version_directory = os.path.join(self.config.default['output_directory'], version)
            file.copy_tree_without_overwrite(self.config.default['input_source_directory'], version_directory, [self.config.default['suffix_source'], self.config.default['suffix_header']])

        # We return a list of generated versions in the output directory.
        return generated_versions

    def execute(self, mode, testmode):
        """
        Method used to start the execution of the main flow.
        :return: nothing.
        """

        # Gather all the source files
        source_files = file.get_files_with_suffix(self.config.default['input_source_directory'], [self.config.default['suffix_source']])

        # We apply the semantic modification tool for source to source transformations.
        print('************ Running semantic-mod tool **********')
        generated_versions = self.execute_semantic_mod(source_files, self.config.semantic_mod['type'])

        if not generated_versions:
            print('************ No versions generated! **********')
            return

        # Gather all version information
        print('************ Gathering version information **********')
        version_information = self.gather_version_information(generated_versions)

        # Do some analysis and find those functions that differ.
        # Make sure there aren't any differences in the data sections.
        print('************ Analyzing differences **********')
        (analytics, functions_diff, data_diff) = self.analyze(source_files, generated_versions, version_information)
        assert not data_diff, 'Differences were introduced in data sections!'

        # In this mode we will stop execution here and output the result as a json file as well.
        if mode == 0:
            # Dump
            with open(os.path.join(self.config.default['output_directory'], 'result.json'), 'w') as f:
                data = dict()
                data["amount_functions"] = analytics["general"]["amount_functions"]
                data["amount_mobile"] = analytics["general"]["amount_mobile"]
                json.dump(data, f, ensure_ascii=False)

        # In this mode we run the ACTC on the rewritten source code, without code mobility.
        elif mode == 1:
            print('************ Running ACTC without CM **********')
            self.run_actc(generated_versions, version_information, set())

        # In this mode we run the ACTC on the rewritten source code, **with** code mobility.
        elif mode == 2:
            print('************ Running ACTC with CM **********')
            self.run_actc(generated_versions, version_information, functions_diff)

            # Sanity check: the protected binaries we generated must be the same
            binaries = [os.path.join(self.actc_.get_output_dir(version), self.config.default['binary_name']) for version in generated_versions]
            assert self.objdump.compare_binaries(binaries), 'Not all protected binaries we generated are the same!'

        # If we are in a mode where binaries are actually created, we can test them.
        if mode and testmode:
            print('************ Testing for correctness **********')
            self.test(generated_versions, testmode)

    def gather_version_information(self, generated_versions):
        # We build a dictionary containing all relevant information of the current version.
        version_information = dict()
        for version in generated_versions:
            # Create dictionary for this specific version. Get some paths and make directories.
            version_dict = version_information[version] = dict()
            version_dict["analysis_directory"] = os.path.join(self.config.default['output_directory'], version + "_analysis")
            version_dict["version_directory"] = os.path.join(self.config.default['output_directory'], version)

            # The first step is to compile all source files into object files in the analysis directory.
            # We compile the source files through a symlink to increase uniformity between
            # the versions and avoid cause data differences between versions because of __FILE__.
            compile_dir = os.path.join(self.config.default['output_directory'], 'uniform_compilation')
            os.symlink(version_dict["version_directory"], compile_dir)
            version_dict["source_files"] = file.get_files_with_suffix(compile_dir, [self.config.default['suffix_source']])
            version_dict["object_files_directory"] = os.path.join(version_dict["analysis_directory"], "objfiles")
            version_dict["object_files"] = file.create_output_paths(version_dict["source_files"], compile_dir, version_dict["object_files_directory"], ".o")
            self.compiler.create_object_files(self.config.actc['common_options'] + self.config.actc['preprocessor_flags'] + self.config.actc['compiler_flags'], version_dict["source_files"], version_dict["object_files"])

            # Generate paths for the analysis files we will generate from the object files.
            version_dict["diss_files"] = file.create_output_paths(version_dict["source_files"], compile_dir, version_dict["object_files_directory"], "_diss.out")
            version_dict["elf_files"] = file.create_output_paths(version_dict["source_files"], compile_dir, version_dict["object_files_directory"], ".elf")
            version_dict["section_files"] = file.create_output_paths(version_dict["source_files"], compile_dir, version_dict["object_files_directory"], ".sections")
            os.remove(compile_dir)

            # We disassemble the generated object files (for DEBUGGING purposes ONLY!), and dump all relevant section information using readelf.
            self.objdump.disassemble_obj_files(self.config.arm_diablo_linux_objdump["base_flags"], version_dict["object_files"], version_dict["diss_files"])
            self.elf_reader.read_files(self.config.elf_reader["base_flags"], version_dict["object_files"], version_dict["elf_files"])

            # We use a custom parser to parse all relevant code (.text) sections
            # out of the ELF files. The result is a list of a list of section names.
            # Every list in the result corresponds to a parsed input file.
            data_sections = parser.Parser.parse_files(version_dict["elf_files"], parser.data_section_extracter, version_dict["section_files"])
            text_sections = parser.Parser.parse_files(version_dict["elf_files"], parser.text_section_extracter, version_dict["section_files"])

            def create_section_dict(version_dict, section_set):
                # We iterate over sets of sections.
                # We are going to store information regarding the different sections in a dictionary.
                # {obj_file_name: (obj_path, {func_name: [sections]})}
                section_info = dict()
                for idx, sect in enumerate(section_set):
                    # We obtain the relative path to the file of the corresponding object file.
                    obj_file_name = os.path.relpath(version_dict["object_files"][idx], version_dict["object_files_directory"])

                    # We create an entry base on the relative path and add a tuple of the full path
                    # and an empty dictionary.
                    section_info[obj_file_name] = (version_dict["object_files"][idx], dict())

                    # We iterate over all sections.
                    for section in sect:
                        # We determine the symbol to which it corresponds.
                        name = sections.extract_symbol_name(section)

                        # We check if the symbol already exists in our dictionary.
                        if name not in section_info[obj_file_name][1]:
                            # We create a new entry containing a single list with the section.
                            section_info[obj_file_name][1][name] = [section]
                        else:
                            # We add the section to the existing list.
                            section_info[obj_file_name][1][name].append(section)

                return section_info

            version_dict["data_section_information"] = create_section_dict(version_dict, data_sections)
            version_dict["text_section_information"] = create_section_dict(version_dict, text_sections)

        return version_information

    def run_actc(self, generated_versions, version_information, functions_diff):
        # The directory in which annotations will be stored.
        annotations_path = os.path.join(self.actc_.path, 'annotations.out')

        # We generate annotations for the functions which have to be made mobile (using a predefined template).
        logging.debug("Creating mobile block annotations...")
        annotations = []
        for function in functions_diff:

            # Function specific annotation.
            annotations.append(templates.read_template_and_fill('function_annotation.template', {'function': function}, None))

        # Write the annotation away in comma-separated style.
        templates.read_template_and_fill('annotations.template', {'functions': ','.join(annotations)}, annotations_path)

        # We will generate ACTC config files for each of the generated versions.
        for version in generated_versions:
            actc_config = os.path.join(self.actc_.path, 'actc.json')
            actual_actc_config = os.path.join(self.actc_.path, version + '.json')
            version_information[version]['actc_config'] = actc_config

            # We need to get all source and header files.
            src_header_files = file.get_files_with_suffix(version_information[version]["version_directory"],
                                                               [self.config.default['suffix_source'],
                                                                self.config.default['suffix_header']])

            # We write the list to a specified format required by the ACTC config file.
            src_header_files_input = ', '.join(["\"" + x + "\"" for x in src_header_files])

            # ACTC configuration file generation (based on a predefined template).
            templates.read_template_and_fill('actc_config.template',
                                        {'binary_name': self.config.default['binary_name'],
                                            'source_code': src_header_files_input,
                                            'annotations': annotations_path,
                                            'common_options': json.dumps(self.config.actc['common_options']),
                                            'compiler_flags': json.dumps(self.config.actc['compiler_flags']),
                                            'linker_flags': json.dumps(self.config.actc['linker_flags']),
                                            'preprocessor_flags': json.dumps(self.config.actc['preprocessor_flags']),
                                            'server': self.config.actc['server']},
                                             actc_config)

            # Now we will employ the ACTC using our mobile block annotations and actc configuration file.
            self.actc_.clean(actc_config)
            self.actc_.execute(actc_config)

            # For all versions we run the ACTC in the same path to avoid any differences in the binary
            # because of __FILE__ being filled in. After running the ACTC we do some renaming to keep
            # the actual ACTC build directory and config around.
            os.rename(self.actc_.get_build_dir('actc'), self.actc_.get_build_dir(version))
            os.rename(actc_config, actual_actc_config)
            version_information[version]['actc_config'] = actual_actc_config

    def test(self, generated_versions, mode):
        # We set up the testing environment locally
        testing_directory = os.path.join(self.config.default['output_directory'], 'testing')
        os.makedirs(testing_directory, exist_ok=True)

        # Do the testing using our own framework
        if mode == 1:
            logging.debug('Testing using our own scripts.')

            # Set the testing environment up remotely
            testing_dir = 'testing'
            test_host = self.config.testing['host']
            logging.debug('Initializing board.')
            subprocess.check_call([os.path.join(testing_dir, 'initialize_board.sh'), test_host, self.config.testing['input_output']])
        # Do the testing using the SPEC framework
        elif mode == 2:
            logging.debug('Testing using the SPEC scripts.')

        # We will now try to deploy all of the versions and corresponding mobile blocks to the testing board.
        for version in generated_versions:
            # We generate the paths for the binary and the mobile blocks (which can be from different versions).
            binary_dir = self.actc_.get_output_dir(version)
            binary = os.path.join(binary_dir, self.config.default['binary_name'])
            mobile_blocks_dir = self.actc_.get_mobile_blocks_dir(version)
            logging.debug('Testing version ' + version + '.')

            # If no blocks were generated, we can't deploy CM
            if os.path.exists(mobile_blocks_dir):
                # Redeploy code mobility to switch blocks (the -i and -p options do not actually matter)
                subprocess.check_call([self.config.actc['deploy_mobility_script'], '-a', self.config.actc['aid'], '-p', '20', '-i', 'localhost', mobile_blocks_dir], stdout=subprocess.DEVNULL)

            # Do the actual test, using either our own script or the SPEC functionality
            if mode == 1:
                subprocess.check_call([os.path.join(testing_dir, 'test_version.sh'), test_host, binary, version, testing_directory])
            elif mode == 2:
                test_dir = os.path.join(testing_directory, version)
                os.makedirs(test_dir)
                spec.test(binary, test_dir, self.config)
