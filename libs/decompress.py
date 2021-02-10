import logging
import subprocess
from libs.command import run_command

password_list = ["终点", "say花火", "www.dreamhouse-seal.vip"]


def guess_password(command):
    for index, password in enumerate(password_list):
        decompress_command = command
        decompress_command.append(f"-p{password}")
        logging.info(f"try to use password: {password}")
        try:
            run_command(decompress_command)
            return True
        except subprocess.CalledProcessError:
            if index == len(password_list) - 1:
                logging.info("all password are wrong, skip this task")
                return False
            else:
                logging.info("maybe wrong password, try to use another password...")
