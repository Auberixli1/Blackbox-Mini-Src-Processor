import logging
import sys
import json
import os
import xml.etree.ElementTree as ElementTree
from pathlib import Path

from Exceptions import SourceEmptyError

VERSION = 0.1

logging.basicConfig(handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ],
    level=logging.ERROR,
    format='%(asctime)s - %(message)s')


def get_directory(root: str, input_dir: str, output_dir: str) -> str:
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


def write_file(data: str, path: str) -> None:
    """
    Used to write the Java Source and the Metadata to the file system.
    :param data: The data in string form that needs to be written
    :param path: The path where the data should be saved
    :return: None
    """
    if not os.path.exists(path):
        try:
            with open(path, 'w') as file:
                file.write(data)
        except EnvironmentError as e:
            # Re-raise exception to catch in callee method.
            raise e
    else:
        logging.info("File already exists: " + path)


def convert_file(root: str, file: str, new_root: str) -> None:
    """
    Converts the SrcML file to raw Java file and writes it to the new directory.
    :param root: The root directory of the old file
    :param file: The file name to convert
    :param new_root: The new root path to save to
    :return: Returns true if an error has occurred, or false if no error has occurred
    """
    xml_tree = ElementTree.parse(os.path.join(root, file)).getroot()

    versions = xml_tree.findall('unit')

    if len(versions) == 0:
        logging.critical("Source file empty: " + root + "/" + file)
        raise SourceEmptyError

    latest_version = versions.pop()

    compile_result = latest_version.attrib['compile-success']

    compile_elements = latest_version.findall('compile-error')

    compile_messages = []
    for element in compile_elements:
        latest_version.remove(element)
        compile_messages.append({
            'message': ElementTree.tostring(element, encoding='unicode', method='text'),
            'start': element.attrib['start'],
            'end': element.attrib['end']
        })

    raw_src = ElementTree.tostring(latest_version, encoding='unicode', method='text')

    metadata = json.dumps({'compile_result': compile_result, 'compile_messages': compile_messages})

    source_file = file.replace(".xml", ".java")
    meta_file = file.replace(".xml", ".json")

    source_path = os.path.join(new_root, source_file)
    meta_path = os.path.join(new_root, meta_file)

    try:
        logging.info("Converting: " + source_path + "/.json")

        write_file(raw_src, source_path)
        write_file(metadata, meta_path)

        logging.info("Converted: " + source_path + "/.json")
    except EnvironmentError as e:
        logging.fatal("ERROR SAVING FILE - Unable to write to file: "
                      "please check permissions and the log file for the exception.")
        logging.fatal(e)
        raise e


def main(input_dir: str, output_dir: str) -> None:
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
        # For each file in partition convert and save
        new_root = get_directory(root, input_dir, output_dir)

        for file in files:
            if file.endswith(".xml"):

                try:
                    convert_file(root, file, new_root)
                except EnvironmentError:
                    logging.fatal("Critical error... Exiting")
                    return
                except SourceEmptyError:
                    logging.critical("Empty source body... Continuing...")

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

