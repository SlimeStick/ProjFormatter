import os.path

from solution import Solution
from trees.props_tree import PropsTree
from trees.vcxproj_tree import VCXProjTree

__all__ = ["format_file"]


def format_file(file_path: str):
    """
    Recursively formats vcxproj and props files.
    :param file_path: Path to a sln or vcxproj or props which will be formatted and searched inside for other files to
    format.
    """
    file_extension = os.path.splitext(file_path)[1]
    if file_extension == ".sln":
        for project_path in Solution(file_path).project_files_absolute_paths():
            format_file(project_path)
    elif file_extension == ".vcxproj":
        VCXProjTree(file_path).format()
    elif file_extension == ".props":
        PropsTree(file_path).format()
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")
