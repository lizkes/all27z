import shutil
import logging
from pathlib import Path
from time import sleep

file_path_list = list()


def get_exact_stem(input_path):
    if input_path.is_file():
        suffixes = input_path.suffixes
        if len(suffixes) > 1 and (
            suffixes[-2].startswith(".part") or suffixes[-2] == ".zip"
        ):
            return input_path.name[: -len("".join(suffixes[-2:]))]
        else:
            return input_path.stem
    else:
        logging.error("input_path must be file")


def traverse(input_path):
    if input_path.is_file():
        suffixes = input_path.suffixes

        # exclude .partX.rar patern, but remain .part1.rar
        if (
            len(suffixes) > 1
            and suffixes[-2].startswith(".part")
            and suffixes[-1] == ".rar"
            and suffixes[-2][5:] != "1"
        ):
            return

        # exclude .zip.XXX patern, but remain .zip.001
        if len(suffixes) > 1 and suffixes[-2] == ".zip" and suffixes[-1] != ".001":
            return

        file_path_list.append(input_path)
    elif input_path.is_dir():
        for child_path in input_path.iterdir():
            traverse(child_path)


def get_file_paths(input_path):
    if input_path.is_dir():
        traverse(input_path)
        return file_path_list
    else:
        logging.error("input_path is not folder")


def rm(path):
    try_count = 10
    while try_count > 0:
        try:
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                elif path.is_file():
                    path.unlink()
                else:
                    logging.warn(f"{path} is not dir or file, can't delete.")
            else:
                logging.debug(f"{path} is not exist, can't delete.")
            break
        except PermissionError as e:
            try_count -= 1
            logging.debug("\n", e, "\nRetry after one second")
            sleep(1)


def rm_content(path):
    if path.is_dir():
        for child in path.iterdir():
            rm(child)
    else:
        logging.error("rm_content: path must be folder")


if __name__ == "__main__":
    import sys

    traverse(Path(sys.argv[1]))
