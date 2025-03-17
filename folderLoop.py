#!/usr/bin/env python3
import subprocess
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Loop through a folder of Ping .bin files and decode each to CSV using a specified decoding script"
    )
    parser.add_argument("folder", help="Folder containing .bin files")
    parser.add_argument("--script", default="decodePing1D_2csv.py",
                        help="Path to the decoding script (default: decodePing1D_2csv.py)")
    args = parser.parse_args()

    folder_path = Path(args.folder)
    # Loop over every .bin file in the folder.
    for bin_file in folder_path.glob("*.bin"):
        input_path = bin_file.resolve()
        # If the bin file is in a folder named "bin", we compute the output folder as its parent's parent / "csv"
        if input_path.parent.name.lower() == "bin":
            output_folder = input_path.parent.parent / "csv"
            output_folder.mkdir(parents=True, exist_ok=True)
            output_csv = output_folder / (input_path.stem + ".csv")
        else:
            # Otherwise, just place the CSV alongside the .bin file.
            output_csv = input_path.with_suffix(".csv")
        
        print(f"Processing {input_path} -> {output_csv}")
        try:
            # Call the decoding script with the input file and computed output file.
            subprocess.run(
                ["python3", args.script, str(input_path), "-o", str(output_csv)],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error processing {input_path}: {e}")

if __name__ == "__main__":
    main()
