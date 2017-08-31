""" Module used for sections functionality. """
import logging


def dump_section(elf_reader, name_section, objectfile):
    """
    Method used to dump a specific section within an object file.
    :param elf_reader: the ELF Reader that will be used to dump the specific section.
    :param name_section: the name of section which will be dumped
    :param objectfile: the object file out of which the section will be extracted.
    :return: the dump of the section.
    """

    # Dump the section from the given object file using objdump.
    flags = ['-x', name_section]
    output = elf_reader.read_file(flags, objectfile)

    # Return the dump.
    return output


def compare_sections(elf_reader, name_section_one, name_section_two, objfile_one, objfile_two):
    """
    Method used to compare two sections of given object files.
    :param elf_reader: the ELF reader that will be used to compare the different sections.
    :param name_section_one: the first section.
    :param name_section_two: the second section.
    :param objfile_one: the object file of the first section.
    :param objfile_two: the object file of the second section.
    :return: True if both sections are equal, False if they are not equal.
    """

    # Debug
    logging.debug("Comparing sections: " + name_section_one + "(" + objfile_one + ") and: " +
                  name_section_two + "(" + objfile_two + ")...")

    # We dump the first section.
    section_one = dump_section(elf_reader, name_section_one, objfile_one)

    # We dump the second section.
    section_two = dump_section(elf_reader, name_section_two, objfile_two)

    # Return True if both sections are equal.
    return section_one == section_two


