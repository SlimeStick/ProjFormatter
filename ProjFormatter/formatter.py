import os.path

from ProjFormatter.trees.props_tree import PropsTree
from ProjFormatter.trees.vcxproj_tree import VCXProjTree

__all__ = ["UnsupportedFileFormat", "format_file", "recursive_format_dir"]


class UnsupportedFileFormat(Exception):
    pass


def format_file(file_path: str):
    """
    Formats a vcxproj or props file.
    :param file_path: Path to a sln or vcxproj or props which will be formatted and searched inside for other files to
    format.
    """
    file_extension = os.path.splitext(file_path)[1]
    if file_extension == ".vcxproj":
        VCXProjTree(file_path).format()
    elif file_extension == ".props":
        PropsTree(file_path).format()
    else:
        raise UnsupportedFileFormat(f"Unsupported file extension: {file_extension}")


def recursive_format_dir(dir_path: str):
    """
    Recursively formats all the props and vcxproj files in a directory.
    """
    for _, _, files in os.walk(dir_path):
        for file in files:
            try:
                format_file(os.path.join(dir_path, file))
            except UnsupportedFileFormat:
                pass
