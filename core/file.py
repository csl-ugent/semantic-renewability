"""
Module used for file related functionality.
"""
import os
import shutil
import json


def discover_subdirectories(path_directory):
    """
    Method used to discover subdirectories (one level deep) in a given directory.
    :param path_directory: the directory in which we will look for subdirectories.
    :return: a list of subdirectory names.
    """
    subdirectories = []

    # We iterate over all files within a given directory.
    for file in os.listdir(path_directory):

        # We generate the full file path.
        file_path = os.path.join(path_directory, file)

        # We check if the file is a directory.
        if os.path.isdir(file_path):
            subdirectories.append(file)
    return subdirectories

def get_files_with_suffix(directory, suffixes):
    # Copy over all files from the source directory, but don't overwrite anything
    source_files = []
    for root, _, files in os.walk(directory):
        for f in files:
            # We check if the file ends with one of the given suffixes.
            for suffix in suffixes:
                if f.endswith(suffix):
                    file_path = os.path.join(root, f)
                    source_files.append(file_path)
                    break
    return source_files

def copy_tree_without_overwrite(src, dst, suffixes=[]):
    """
    Method used to copy files from one directory structure to another based on the fact that a files
    does not already exist in the other directory structure.
    :param src: the directory from which we are copying.
    :param dst: the directory to which we are copying.
    :return:
    """
    # Copy over all files from the source directory, but don't overwrite anything
    for root, _, files in os.walk(src):
        relpath = os.path.relpath(root, src)
        dst_dir = os.path.join(dst, relpath)
        for f in files:
            # If any suffixes were specified, we want to check whether we are supposed to copy this file
            copy = not suffixes
            for suffix in suffixes:
                if f.endswith(suffix):
                    copy = True
                    break

            if not copy:
                continue

            # Don't overwrite files
            copy = not os.path.exists(os.path.join(dst_dir, f))

            # Do the actual copy, creating the intermediary directories
            if copy:
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                shutil.copy(os.path.join(root, f), dst_dir)

def create_output_paths(source_files, base_directory_from, base_directory_to, suffix):
    """
    Method used to create a list of output paths based on an input of source files, a base output
    path and a new suffix for the existing source files.
    :param source_files: the input list of files (absolute paths).
    :param base_directory_from: the base directory in which all source files are located.
    :param base_directory_to: the base directory to which all source files should be copied (relatively)
    :param suffix: the new suffix for the given source files.
    :return: a list of absolute paths of the source files in the destination directory with application of
    the new suffix.
    """
    # Iterate over all source files (absolute paths).
    output_paths = []
    for source_file in source_files:

        # First we need to extract the relative path of the source files (relative to the base_directory_from)
        rel_str = obtain_rel_path(source_file, base_directory_from)

        # We need to change the suffix of the file.
        new_rel_str = change_suffix_file(rel_str, suffix)

        # We construct the new absolute path based on the base directory destination.
        new_full_path = os.path.join(base_directory_to, new_rel_str)

        # We have to create directories if required.
        os.makedirs(os.path.dirname(new_full_path), exist_ok=True)

        # We append the new full path to the output paths.
        output_paths.append(new_full_path)

    # We return the list of output paths.
    return output_paths


def change_suffix_file(file_name, new_suffix):
    """
    Method used to change the suffix of a given filename to a new suffix.
    :param file_name: the filename of which the suffix has to be changed.
    :param new_suffix: the new suffix of the filename.
    :return: the changed file_name.
    """
    return file_name.rsplit(sep='.', maxsplit=1)[0] + new_suffix


def obtain_rel_path(full_path, base_path):
    """
    Method used to obtain the relative path of a specified file on a full path, relative
    to the given base path.
    :param full_path: the full path of the file we are going to determine the relative path of.
    :param base_path: the base path relative to which we consider the file.
    :return: relative path of given file to base path.
    """
    return full_path[len(base_path)+1:]


def read_json(full_path):
    """
    Method used to read a JSON file.
    :param full_path: the absolute path where the JSON file can be found.
    :return: the JSON file content as a dictionary object.
    """
    data_json = dict()
    with open(full_path) as data_file:
        data_json = json.load(data_file)
    return data_json
