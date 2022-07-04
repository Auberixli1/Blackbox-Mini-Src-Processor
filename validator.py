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


def main(input_dir, output_dir):
    logging.info("Finding files")

    input_reg = re.compile("^" + input_dir + "((/[A-Za-z0-9-]+)+).xml")
    output_reg = re.compile("^" + output_dir + "((/[A-Za-z0-9\-]+)+)\.(java|json)")

    input_files = (re.match(input_reg, os.path.join(root, file)).group(1)
                   for root, _, files in os.walk(input_dir)
                   for file in files if file.endswith(".xml"))

    source_files = (re.match(output_reg, os.path.join(root, file)).group(1)
                   for root, _, files in os.walk(output_dir)
                   for file in files if file.endswith(".java"))

    meta_files = (re.match(output_reg, os.path.join(root, file)).group(1)
                    for root, _, files in os.walk(output_dir)
                    for file in files if file.endswith(".json"))

    logging.info("Found all files. Calculating difference...")

    source_diff = set(input_files) - set(source_files)
    meta_diff = set(input_files) - set(meta_files)

    logging.info("Missing Source files: " + " ".join(source_diff))
    logging.info("Missing Meta files: " + " ".join(meta_diff))
    logging.info("Difference between source and meta: " + " ".join(source_diff - meta_diff))


if __name__ == '__main__':
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if "-v" in opts or "--verbose" in opts:
        logging.getLogger().setLevel(logging.INFO)
    if "--version" in opts:
        print(VERSION)

    if len(args) != 2:
        print("Please add the input and output directoies you need to valdate.")
        print("python3 validator.py /data/mini /data/minisrc")
        print("Use -v to enable logging")
        logging.info("Not enough arguments to start process")
    else:
        main(input_dir=args[0], output_dir=args[1])
