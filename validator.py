import filecmp
import os.path
import sys
import logging
import re

logging.basicConfig(handlers=[
    logging.FileHandler("debug.log"),
    logging.StreamHandler()
],
    level=logging.ERROR,
    format='%(asctime)s - %(message)s')

VERSION = 0.1


def find_diff(input_dir, output_dir):
    input_subdirs = set(filter(os.path.isdir, os.listdir(input_dir)))
    dir_cmp = filecmp.dircmp(input_dir, output_dir)

    diff = input_subdirs - set(dir_cmp.common_dirs)

    logging.debug("Difference between: " + input_dir + " and " + output_dir + ":\n" + str(diff))

    if len(diff) > 0:
        print("Difference between: " + input_dir + " and " + output_dir + ":\n" + str(diff))
    else:
        logging.debug("No difference between " + input_dir + " and " + output_dir)


def main(input_dir, output_dir):
    logging.info("Finding files")

    find_diff(input_dir, output_dir)

    for root, dirs, _ in os.walk(input_dir):
        new_root = root.replace(input_dir, output_dir)
        find_diff(root, new_root)



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
