"""Module responsible for template reading."""
import os

# Path to folder containing all templates.
TEMPLATE_PATH = "templates"

def read_template_and_fill(template_name, data, file_path=None):
    """
    Method used to read a template and fill it in using the given data.
    :param template_name: the name of the template available in the template directory.
    :param data: a dictionary containing the parameters and values which have to be filled in.
    :param file_path: a possible location to save the output of the filled in template.
    :return: the full filled in template content.
    """
    # We read out the specified template.
    with open(os.path.join(TEMPLATE_PATH, template_name), "r") as fp:

        # We read in the whole template.
        template_content = fp.read()

        # We fill in the template content using the data provided.
        template_content = template_content.format(**data)

    # Optional writing template to a given file path.
    if file_path is not None:

        # Optional creating directory (if necessary)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as fp:

            # We write the template content to the given file path.
            fp.write(template_content)

    # We return the filled in template content.
    return template_content
