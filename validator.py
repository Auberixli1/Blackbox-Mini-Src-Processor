import filecmp
import os.path
import sys
import logging
import multiprocessing as mp
from multiprocessing_logging import install_mp_handler

logging.basicConfig(handlers=[
    logging.FileHandler("debug.log"),
    logging.StreamHandler()
],
    level=logging.ERROR,
    format='%(processName)s - %(asctime)s - %(message)s')

install_mp_handler()

VERSION = 0.1
MULTIPROCESS_DIVISOR = 4


def process_directory(input_dir: str, output_dir: str, input_subdirs: list) -> None:
    """
    Search for missing subdirectories
    :param input_dir: The input directory to validate against
    :param output_dir: The output directory to search
    :param input_subdirs: The list of sub-directories in the input directory
    :return: None
    """
    dir_cmp = filecmp.dircmp(input_dir, output_dir)

    diff = set(input_subdirs) - set(dir_cmp.common_dirs)

    if len(diff) > 0:
        print("Difference between: " + input_dir + " and " + output_dir + "(" + str(len(diff)) + ")")
        logging.info("Difference between: " + input_dir + " and " + output_dir + "(" + str(len(diff)) + ")\n" + str(diff))
    else:
        logging.debug("No difference between " + input_dir + " and " + output_dir)


def process_file(input_dir: str, output_dir: str) -> None:
    """
    Search for missing files
    :param input_dir: The input directory to validate against
    :param output_dir: The output directory to search
    :return: None
    """
    input_files = set([f.replace(".xml", "") for f in os.listdir(input_dir) if f.endswith(".xml")])

    source_files = []
    meta_files = []

    for f in os.listdir(output_dir):
        if f.endswith(".java"):
            source_files.append(f.replace(".java", ""))
        elif f.endswith(".json"):
            meta_files.append(f.replace(".json", ""))

    source_diff = input_files - set(source_files)
    meta_diff = input_files - set(meta_files)

    if len(source_diff) > 0:
        print("Missing source files in: " + output_dir + ":\n" + str(source_diff))
        logging.info("Missing source files in: " + output_dir + ":\n" + str(source_diff))
    else:
        logging.debug("No missing source files in: " + output_dir)

    if len(meta_diff) > 0:
        print("Missing meta files: " + output_dir + ":\n" + str(meta_diff))
        logging.info("Missing meta files: " + output_dir + ":\n" + str(meta_diff))
    else:
        logging.debug("No missing meta files in: " + output_dir)


def find_diff(input_dir: str, output_dir: str, input_subdirs: list) -> None:
    """
    Processor to find the difference for lists of directories and files
    :param input_dir: The input directory to validate against
    :param output_dir: The output directory to search
    :param input_subdirs: The list of sub-directories in the input directory
    :return: None
    """
    if len(input_subdirs) == 0:
        if os.path.exists(input_dir) and os.path.exists(output_dir):
            logging.debug("Processing files")
            process_file(input_dir, output_dir)
        else:
            print("Directory does not exist: " + input_dir + ":" + output_dir)
            logging.info("Directory does not exist: " + input_dir + ":" + output_dir)
    else:
        logging.debug("Processing directory")
        process_directory(input_dir, output_dir, input_subdirs)


def main(input_dir: str, output_dir: str) -> None:
    """
    Splits search between different processes, searches for any missing directorties or files.
    :param input_dir: The input directory to validate against
    :param output_dir: The output directort to validate
    :return: None
    """
    logging.info("Finding files")

    pool = mp.Pool(mp.cpu_count() // MULTIPROCESS_DIVISOR)

    for root, dirs, _ in os.walk(input_dir):
        new_root = root.replace(input_dir, output_dir)
        pool.apply(find_diff, args=(root, new_root, dirs))

    pool.close()
    print("Complete")



if __name__ == '__main__':
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if "-v" in opts or "--verbose" in opts:
        logging.getLogger().setLevel(logging.INFO)
    if "-vv" in opts:
        logging.getLogger().setLevel(logging.DEBUG)
    if "--version" in opts:
        print(VERSION)

    if len(args) != 2:
        print("Please add the input and output directoies you need to valdate.")
        print("python3 validator.py /data/mini /data/minisrc")
        print("Use -v to enable logging")
        logging.info("Not enough arguments to start process")
    else:
        main(input_dir=args[0], output_dir=args[1])
