import core.command as cmd
import core.tools.util as util
import logging
import os

# Path to folder containing all scripts.
SCRIPTS_PATH = "scripts"


def execute_scripts(script_name, arguments):

    # Debug information
    logging.debug("Executing script: " + script_name)

    # We build the command to be executed.
    command_exec = ['bash', os.path.join(SCRIPTS_PATH, script_name)] + arguments

    # We execute the command.
    (status, stdout, stderr) = cmd.execute_command_status_output(command_exec)
    util.handle_status(status, stdout, stderr)