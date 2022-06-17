import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

VERSION = 0.1


def get_directory(root, org_dir, src_dir):
    """
    Used to transform the original directory to the new directory, and creates the directory if needed
    :param root: Root directory to convert
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

    xml_tree = ET.parse(os.path.join(root, file))
    raw_src = ET.tostring(xml_tree.getroot(), encoding='unicode', method='text')

    new_file = file.replace(".xml", ".java")

    new_path = os.path.join(new_root, new_file)
    if not os.path.exists(new_path):
        try:
            with open(new_path, 'w') as f:
                f.write(raw_src)
        except EnvironmentError:
            print("Unable to write to file, please check permissions and the log file for the exception.")
            # TODO log excpetion
            return True


def main(org_dir, src_dir):
    """
    Main processor for converting SrcML to raw source.
    :param org_dir: The original directory to convert
    :param src_dir: The directory to save the Java files to.
    :return: None
    """
    assert os.path.isdir(org_dir)
    assert os.path.isdir(src_dir)

    for root, dirs, files in os.walk(org_dir):
        # For each file in partition convert and save
        new_root = get_directory(root, org_dir, src_dir)

        for file in files:
            if file.endswith(".xml"):
                is_error = convert_file(root, file, new_root)

                if is_error:
                    # End program
                    return
                
                return
            

if __name__ == '__main__':

    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if len(args) != 2:
        print("Please add the directory to convert and the directory you want to save to.")
        print("python3 processor.py /data/mini /data/minisrc")
        print("Use -v to enable logging")
    else:
        if "-v" or "--verbose" in opts:
            print("VERBOSE")
            pass
        if "--version" in opts:
            print(VERSION)

        main(org_dir=args[0], src_dir=args[1])
