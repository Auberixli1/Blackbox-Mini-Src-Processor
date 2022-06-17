import logging
import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

VERSION = 0.1

logging.basicConfig(handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ],
    level=logging.ERROR,
    format='%(asctime)s - %(message)s')


def get_directory(root, org_dir, src_dir):
    """
    Used to transform the original directory to the new directory, and creates the directory if needed
    :param root: Root directory to convert
    :param org_dir: The directory to convert from
    :param src_dir: The directory to save to
    :return: New directory
    """

    new_root = root.replace(org_dir, src_dir)

    if not os.path.exists(new_root):
        Path(new_root).mkdir(parents=True, exist_ok=True)

    return new_root


def convert_file(root, file, new_root):
    """
    Converts the SrcML file to raw Java file and writes it to the new directory.
    :param root: The root directory of the old file
    :param file: The file name to convert
    :param new_root: The new root path to save to
    :return: None
    """
    xml_tree = ET.parse(os.path.join(root, file)).getroot()
    latest_version = xml_tree.findall('unit').pop()

    raw_src = ET.tostring(latest_version, encoding='unicode', method='text')

    new_file = file.replace(".xml", ".java")

    new_path = os.path.join(new_root, new_file)
    logging.info("Converting: " + new_path)

    if not os.path.exists(new_path):
        try:
            with open(new_path, 'w') as f:
                f.write(raw_src)
        except EnvironmentError as e:
            logging.fatal("ERROR SAVING FILE - Unable to write to file, "
                          "please check permissions and the log file for the exception.")
            logging.fatal(e)
            return True


def main(org_dir, src_dir):
    """
    Main processor for converting SrcML to raw source.
    :param org_dir: The original directory to convert
    :param src_dir: The directory to save the Java files to.
    :return: None
    """
    if not os.path.isdir(org_dir) or not os.path.isdir(src_dir):
        logging.fatal("Either the origin directory or the destination directory are not valid")
        return

    count = 0
    for root, dirs, files in os.walk(org_dir):
        print(files)
        # For each file in partition convert and save
        new_root = get_directory(root, org_dir, src_dir)

        for file in files:
            if file.endswith(".xml"):
                is_error = convert_file(root, file, new_root)

                if is_error:
                    logging.fatal("Critical error... Exiting")

    print("Complete, new files are in", args[1])
            

if __name__ == '__main__':

    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if "-v" in opts or "--verbose" in opts:
        logging.getLogger().setLevel(logging.INFO)
    if "--version" in opts:
        print(VERSION)

    if len(args) != 2:
        print("Please add the directory to convert and the directory you want to save to.")
        print("python3 processor.py /data/mini /data/minisrc")
        print("Use -v to enable logging")
        logging.info("Not enough arguments to start process")
    else:
        main(org_dir=args[0], src_dir=args[1])

