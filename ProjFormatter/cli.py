import argparse
from formatter import format_file

def main():
    parser = argparse.ArgumentParser(description="Recursively format vcxproj and props files.")
    parser.add_argument("file", type=str,
                        help="Path to a sln or vcxproj or props which will be formatted and searched inside for other "
                             "files to format.")
    args = parser.parse_args()
    format_file(args.file)

if __name__ == "__main__":
    main()
