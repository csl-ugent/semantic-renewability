"""
Module handling the execution of commands.
"""
from subprocess import Popen, PIPE
import logging


def execute_command_status_output(command, out=PIPE):
    """
    :param command: the full cmd command to be executed.
    :return: (stdout, ret_code).
    """
    logging.debug("Executing command: " + str(" ".join(command)))

    # Command execution itself.
    p = Popen(command, stdout=out if out is not None else PIPE, stderr=PIPE)
    stdout = ""
    (stdout, stderr) = p.communicate()
    ret_code = p.returncode
    logging.debug("ret code: " + str(ret_code))
    if stdout is not None:
        logging.debug("stdout: " + stdout.decode("utf-8"))
    if stderr is not None:
        logging.debug("stderr: " + stderr.decode("utf-8"))
    return ret_code, stdout, stderr
