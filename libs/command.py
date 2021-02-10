import subprocess
import logging


def run_command(command):
    logging.debug(f"run command: {command}")
    subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True
    )