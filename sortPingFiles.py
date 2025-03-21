#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
from decode_sensor_binary_log import PingViewerLogReader

def determine_file_type(file_path):
    """
    Try to open the bin file and inspect the first decoded message.
    Returns:
      - "ping1D" if the first message's ID is in {1211, 1212, 1300}
      - "ping360" if it is in {2300, 2301}
      - None if it cannot be determined.
    """
    try:
        # Create a log reader for the file.
        log = PingViewerLogReader(str(file_path))
        for timestamp, decoded_message in log.parser():
            mid = decoded_message.message_id
            if mid in {1211, 1212, 1300}:
                return "ping1D"
            elif mid in {2300, 2301}:
                return "ping360"
            # If the first message doesn't match either set, continue looking.
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return None

def main():
    # Define folder paths (update these paths to your actual folders)
    input_folder = "/Users/courtneyanderson/Downloads/projects/BlueRov/KeckTest/Data/PingView"
    output_folder_ping1D = "/Users/courtneyanderson/Downloads/projects/BlueRov/KeckTest/Data/1D"
    output_folder_ping360 = "/Users/courtneyanderson/Downloads/projects/BlueRov/KeckTest/Data/360"

    # Create output folders if they don't exist.
    os.makedirs(output_folder_ping1D, exist_ok=True)
    os.makedirs(output_folder_ping360, exist_ok=True)

    # Loop over all .bin files in the input folder.
    for file_path in Path(input_folder).glob("*.bin"):
        file_type = determine_file_type(file_path)
        if file_type == "ping1D":
            dest = Path(output_folder_ping1D) / file_path.name
            shutil.move(str(file_path), str(dest))
            print(f"Moved {file_path.name} to {output_folder_ping1D}")
        elif file_type == "ping360":
            dest = Path(output_folder_ping360) / file_path.name
            shutil.move(str(file_path), str(dest))
            print(f"Moved {file_path.name} to {output_folder_ping360}")
        else:
            print(f"Could not determine file type for {file_path.name}")

if __name__ == "__main__":
    main()
