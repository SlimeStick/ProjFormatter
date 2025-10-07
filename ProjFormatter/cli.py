import argparse
import os.path

from ProjFormatter.formatter import format_file, recursive_format_dir


def main():
    parser = argparse.ArgumentParser(description="""Recursively format vcxproj and props files.
Supports configuration from multiple sources, applied in this order of priority:
    1. CLI flags
    2. Project configuration file (projformatter.toml)
    3. User configuration file (C:/Users/<username>/projformatter/config.toml)
    4. Built-in defaults
""",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", type=str,
                        help="Path to a vcxproj or props file to format or a path to a directory in which all props and"
                             " vcxproj files will be formatted recursively.")
    args = parser.parse_args()
    if os.path.isfile(args.file):
        format_file(args.file)
    elif os.path.isdir(args.file):
        recursive_format_dir(args.file)
    else:
        raise ValueError("The given path is not a file or a directory.")


if __name__ == "__main__":
    main()
