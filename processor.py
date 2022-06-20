import logging
import sys
import textwrap
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString
import os
import xml.etree.ElementTree as ElementTree
from pathlib import Path

VERSION = 0.1

logging.basicConfig(handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ],
    level=logging.ERROR,
    format='%(asctime)s - %(message)s')

"""
Setup the YAML library, to enable dumping the processed to a readable YAML format
"""
yaml = YAML()


def multiline_handler(string):
    """
    Used to convert a multiline string into a readable YAML format.
    Adapted from: https://stackoverflow.com/questions/57382525/can-i-control-the-formatting-of-multiline-strings
    :param string: The multiline string to convert
    :return: The multiline string in the YAML literal style
    """
    return LiteralScalarString(textwrap.dedent(string))


def get_directory(root, input_dir, output_dir):
    """
    Used to transform the original directory to the new directory, and creates the directory if needed
    :param root: Root directory to convert
    :param input_dir: The directory to convert from
    :param output_dir: The directory to save to
    :return: New directory
    """

    new_root = root.replace(input_dir, output_dir)

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
    xml_tree = ElementTree.parse(os.path.join(root, file)).getroot()
    latest_version = xml_tree.findall('unit').pop()

    compile_result = latest_version.attrib['compile-success']

    compile_element = latest_version.find('./compile-error')

    if compile_element is None:
        compile_message = None
    else:
        latest_version.remove(compile_element)
        compile_message = ElementTree.tostring(compile_element, encoding='unicode',method='text')

    raw_src = ElementTree.tostring(latest_version, encoding='unicode', method='text')

    output_dict = {'compile_result': compile_result, 'compile_message': compile_message,
                   'source': multiline_handler(raw_src)}

    new_file = file.replace(".xml", ".yaml")

    new_path = os.path.join(new_root, new_file)
    logging.info("Converting: " + new_path)

    if not os.path.exists(new_path):
        try:
            with open(new_path, 'w') as output_file:
                yaml.dump(output_dict, output_file)
                logging.info("Converted: " + new_path)
        except EnvironmentError as e:
            logging.fatal("ERROR SAVING FILE - Unable to write to file, "
                          "please check permissions and the log file for the exception.")
            logging.fatal(e)
            return True
    else:
        logging.info("File already exists: " + new_path)


def main(input_dir, output_dir):
    """
    Main processor for converting SrcML to raw source.
    :param input_dir: The original directory to convert
    :param output_dir: The directory to save the Java files to.
    :return: None
    """
    if not os.path.isdir(input_dir):
        logging.fatal("Either the origin directory or the destination directory are not valid")
        return

    for root, dirs, files in os.walk(input_dir):
        print(files)
        # For each file in partition convert and save
        new_root = get_directory(root, input_dir, output_dir)

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
        main(input_dir=args[0], output_dir=args[1])

