import argparse
import os.path

from ProjFormatter.formatter import format_file, recursive_format_dir


def main():
    parser = argparse.ArgumentParser(description="Recursively format vcxproj and props files.")
    parser.add_argument("file", type=str,
                        help="Path to a vcxproj or props file to format or a path to a directory in which all props and"
                             " vcxproj files will be formatted recursively.")
    args = parser.parse_args()
    if os.path.isfile(args.file):
        format_file(args.file)
    else:
        recursive_format_dir(args.file)


if __name__ == "__main__":
    main()
