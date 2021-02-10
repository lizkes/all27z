import logging
import atexit
import argparse
import subprocess
from pathlib import Path

from libs.command import run_command
from libs.decompress import guess_password
from libs.file import get_file_paths, get_exact_stem, rm, rm_content

# init logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%y/%m/%d %H:%M:%S",
)

# init argparse
parser = argparse.ArgumentParser(
    prog="all27z", description="convert all compressed file to 7z"
)
parser.add_argument("input", help="input file or folder")
parser.add_argument("output", help="output folder")
parser.add_argument(
    "-p",
    "--password",
    dest="password",
    help="decompress password, if not specified, no password will be used",
)
parser.add_argument(
    "-c",
    "--core",
    dest="core",
    help="cpu core used in compress, if not specified, use all",
)
parser.add_argument(
    "-rm",
    "--remove_origin",
    action="store_true",
    dest="remove_origin",
    help="Whether to delete the original file or folder",
)
args = parser.parse_args()

# global variable
SUPPORT_FORMAT = ["zip", "rar", "xz", "bz2", "gz", "tar", "wim"]
input_path = Path(args.input).resolve()
output_path = Path(args.output).resolve()
seven_zip_path = Path(__file__).parent.joinpath("bin", "7z.exe")
if input_path.is_file():
    temp_dir_path = Path(input_path.parent.joinpath("all27z_temp"))
elif input_path.is_dir():
    temp_dir_path = Path(input_path.joinpath("all27z_temp"))


def process_file(input_path):
    if input_path.suffix[1:] not in SUPPORT_FORMAT:
        logging.error(f"the format of input file is not support: {input_path}, skip...")
        return
    # make decompress command
    # https://sevenzip.osdn.jp/chm/cmdline/commands/extract_full.htm
    decompress_command = [
        seven_zip_path.as_posix(),
        "x",
        f"{input_path.as_posix()}",
        f"-o{temp_dir_path.as_posix()}",
        "-aoa",
    ]
    if args.password:
        decompress_command.append(f"-p{args.password}")
    else:
        decompress_command.append("-p")

    # start decompress
    logging.info(f"Start decompress {input_path.as_posix()}")
    try:
        run_command(decompress_command)
    except subprocess.CalledProcessError:
        logging.info("maybe wrong password, try to guess password...")
        result = guess_password(decompress_command[:-1])
        if result is False:
            rm_content(temp_dir_path)
            logging.debug(f"temp dir content has been deleted: {temp_dir_path}")

    logging.info(f"Complete decompress {input_path.as_posix()}")
    # make compress command
    # https://sevenzip.osdn.jp/chm/cmdline/commands/add.htm
    output_file_path_str = output_path.joinpath(
        f"{get_exact_stem(input_path)}.7z"
    ).as_posix()
    compress_command = [
        seven_zip_path.as_posix(),
        "a",
        f"{output_file_path_str}",
        f"{temp_dir_path.as_posix()}\\*",
        "-mx=9",
        "-myx=9",
        "-mqs=on",
        "-sdel",
    ]
    if args.core:
        compress_command.append(f"-mmt={args.core}")
    else:
        compress_command.append("-mmt=on")

    # start compress
    logging.info(f"start compress {output_file_path_str}")
    run_command(compress_command)
    logging.info(f"Complete compress {output_file_path_str}")


if __name__ == "__main__":
    temp_dir_path.mkdir(parents=True, exist_ok=True)
    logging.debug(f"temp dir {temp_dir_path} has been created")

    def exit_handler():
        rm(temp_dir_path)
        logging.debug(f"temp dir {temp_dir_path} has been deleted")
        if args.remove_origin:
            rm(input_path)
            logging.info(f"input has been deleted: {input_path.as_posix()}")

    atexit.register(exit_handler)

    if input_path.is_file():
        process_file(input_path)
    elif input_path.is_dir():
        file_paths = get_file_paths(input_path)
        for file_path in file_paths:
            process_file(file_path)
    else:
        logging.error(f"input {args.input} must be file or folder")
