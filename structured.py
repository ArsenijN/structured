import os
import hashlib
import datetime
import argparse
import configparser

def get_file_hash(file_path, hash_function):
    """Compute the hash of a file using the specified hash function."""
    hasher = hashlib.new(hash_function)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def format_size(size, mode):
    """Format file size based on the mode."""
    if mode == "1":  # Mixed unit hierarchy
        units = ['B', 'kB', 'MB', 'GB', 'TB']
        result = []
        for unit in units:
            if size == 0:
                break
            size, rem = divmod(size, 1024)
            if rem > 0 or unit == 'B':  # Always include remainder or exact bytes
                result.append(f"{rem} {unit}")
        return ", ".join(reversed(result))

    elif mode == "2":  # Exact bytes only
        return f"{size:,} B"  # Include thousands separator for readability

    else:
        raise ValueError("Invalid size format mode. Expected '1' or '2'.")

def generate_file_list(base_dir, output_path, hash_function="md5", size_format="1", mode="w"):
    """Generate a list of files with their metadata and hash."""
    with open(output_path, mode, encoding="utf-8") as output_file:
        if mode == "w":
            # Write the header only if overwriting
            output_file.write(f"Full path/file | Time of file edit | Size | {hash_function.upper()}\n")

        # Walk through the directory recursively
        for root, _, files in os.walk(base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, base_dir)
                
                # print(edit_time_enable)
                # print(size_enable)
                # print(hash_enable)
                
                if not edit_time_enable == "False":
                    edit_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    edit_time = "-"

                if not size_enable == "False":
                    size = os.path.getsize(file_path)
                    size_display = format_size(size, size_format)
                else:
                    size_display = "-"
                
                if not hash_enable == "False":
                    hash_value = get_file_hash(file_path, hash_function)
                else:
                    hash_value = "-"

                # Write file info to output
                output_file.write(f"{relative_path} | {edit_time} | {size_display} | {hash_value}\n")

def read_settings(settings_path):
    """Read settings from the settings.ini file."""
    config = configparser.ConfigParser()
    if not os.path.exists(settings_path):
        raise FileNotFoundError(f"Settings file not found: {settings_path}")
    config.read(settings_path)
    hash_function = config.get("Settings", "hash_function", fallback="md5")
    size_format = config.get("Settings", "size_format", fallback="1")
    
    hash_enable = config.get("Settings", "hash_enable", fallback=True)
    edit_time_enable = config.get("Settings", "edit_time_enable", fallback=True)
    size_enable = config.get("Settings", "size_enable", fallback=True)
    return hash_function, size_format, hash_enable, edit_time_enable, size_enable

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List all files in a directory and export their metadata and hash.")
    parser.add_argument("directory", nargs="?", default=None, help="Directory to scan (default: current working directory)")
    args = parser.parse_args()

    # Determine the directory to scan
    directory = args.directory or os.getcwd()

    # Path to the settings.ini file
    settings_file = os.path.join(os.path.dirname(__file__), "settings.ini")

    try:
        # Read settings from settings.ini
        hash_function, size_format, hash_enable, edit_time_enable, size_enable = read_settings(settings_file)
        # Validate hash function
        hashlib.new(hash_function)
        # Validate size format
        if size_format not in ["1", "2"]:
            raise ValueError("Invalid size format mode in settings.ini. Must be '1' or '2'.")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        exit(1)

    # Determine the output file path
    output_file = os.path.join(directory, "structure.txt")

    # Check if the file exists and handle user input
    if os.path.exists(output_file):
        print(f"{output_file} already exists.")
        print("Choose an option:")
        print("1. Append")
        print("2. Overwrite")
        print("3. Skip (exit)")
        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            mode = "a"  # Append
        elif choice == "2":
            mode = "w"  # Overwrite
        elif choice == "3":
            print("Exiting without changes.")
            exit(0)
        else:
            print("Invalid choice. Exiting.")
            exit(1)
    else:
        mode = "w"  # Create a new file

    # Generate the file list
    generate_file_list(directory, output_file, hash_function, size_format, mode)
    print(f"File list saved to {output_file}.")
