import argparse
import os

def format_sln(file, fix_guids, sort_projects):
    print(f"Formatting SLN file: {file}")
    if fix_guids:
        print("Fixing GUIDs")
    if sort_projects:
        print("Sorting projects")

def format_vcxproj(file, remove_unused, normalize_paths):
    print(f"Formatting VCXPROJ file: {file}")
    if remove_unused:
        print("Removing unused includes")
    if normalize_paths:
        print("Normalizing paths")

def format_props(file, sort_properties, clean_empty):
    print(f"Formatting PROPS file: {file}")
    if sort_properties:
        print("Sorting properties")
    if clean_empty:
        print("Cleaning empty groups")

def main():
    base_parser = argparse.ArgumentParser(
        description="Format .sln, .vcxproj, or .props files automatically based on extension"
    )
    base_parser.add_argument("file", help="Path to the file to format")
    # Parse only the file path first
    base_arguments, remaining_argv = base_parser.parse_known_args()

    file_extension = os.path.splitext(base_arguments.file)[1]

    # Create subparser based on file extension
    if file_extension == ".sln":
        parser = argparse.ArgumentParser(
            description="Format a .sln file"
        )
        parser.add_argument("--fix-guids", action="store_true", help="Fix mismatched GUIDs")
        parser.add_argument("--sort-projects", action="store_true", help="Sort projects alphabetically")
        parser.set_defaults(func=format_sln)

    elif file_extension == ".vcxproj":
        parser = argparse.ArgumentParser(
            description="Format a .vcxproj file"
        )
        parser.add_argument("--remove-unused", action="store_true", help="Remove unused includes")
        parser.add_argument("--normalize-paths", action="store_true", help="Normalize include/library paths")
        parser.set_defaults(func=format_vcxproj)

    elif file_extension == ".props":
        parser = argparse.ArgumentParser(
            description="Format a .props file"
        )
        parser.add_argument("--sort-properties", action="store_true", help="Sort properties alphabetically")
        parser.add_argument("--clean-empty", action="store_true", help="Remove empty property groups")
        parser.set_defaults(func=format_props)

    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

    full_args = parser.parse_args()
    full_args.func(full_args)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
