import os
import xml.etree.ElementTree as ET
from pathlib import Path

MINI_DIRECTORY = "/data/mini"
MINI_SRC_DIRECTORY = "/data/minisrc"


def get_directory(root):
    """
    Used to convert the mini directory to the mini src directory, and creates the directory if needed
    :param root: Root directory to convert
    :return: New directory
    """

    new_root = root.replace(MINI_DIRECTORY, MINI_SRC_DIRECTORY)

    if not os.path.exists(new_root):
        Path(new_root).mkdir(parents=True, exist_ok=True)

    return new_root


def convert_file(root, file):
    """
    Converts the SrcML file to raw Java file and writes it to the new directory.
    :param root: The root directory of the old file
    :param file: The file name to convert
    :return: None
    """
    new_root = get_directory(root)

    xml_tree = ET.parse(os.path.join(root, file))
    raw_src = ET.tostring(xml_tree.getroot(), encoding='unicode', method='text')

    new_file = file.replace(".xml", ".java")

    new_path = os.path.join(new_root, new_file)
    if not os.path.exists(new_path):
        with open(new_path, 'w') as f:
            f.write(raw_src)


def main():
    """
    Main processor for converting SrcML to raw source.
    :return:
    """
    assert os.path.isdir(MINI_DIRECTORY)
    assert os.path.isdir(MINI_SRC_DIRECTORY)

    for root, dirs, files in os.walk(MINI_DIRECTORY):
        # For each file in partition convert and save
        for file in files:
            if file.endswith(".xml"):
                convert_file(root, file)
                
                return
            

if __name__ == '__main__':
    main()
