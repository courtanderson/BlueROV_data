#!/usr/bin/env python3
import csv
import argparse
import pandas as pd
from datetime import time, timedelta
from pathlib import Path
from decode_sensor_binary_log import PingViewerLogReader

def parse_timestamp(timestamp_str):
    """
    Remove null bytes and convert a timestamp string in the format 'hh:mm:ss.xxx'
    into a timedelta.
    """
    clean_str = timestamp_str.replace('\x00', '')
    t_obj = time.fromisoformat(clean_str)
    return timedelta(hours=t_obj.hour, minutes=t_obj.minute,
                     seconds=t_obj.second, microseconds=t_obj.microsecond)

def main():
    parser = argparse.ArgumentParser(
        description="Decode Ping1D binary file and output sonar data to CSV with real timestamps"
    )
    parser.add_argument("file", help="Input binary file containing Ping1D data")
    parser.add_argument("-o", "--output", default="",
                        help="(Optional) Output CSV file. If not provided, CSV file is written to adjacent 'csv' folder.")
    args = parser.parse_args()

    input_path = Path(args.file)
    # Determine the output file.
    if args.output:
        output_csv = Path(args.output)
    else:
        # Assume input is in .../bin/ so output will be in .../csv/ with the same stem.
        csv_folder = input_path.parent.parent / "csv"
        csv_folder.mkdir(parents=True, exist_ok=True)
        output_csv = csv_folder / (input_path.stem + ".csv")
    
    # Calculate the base time from the file's stem.
    base_time = pd.to_datetime(input_path.stem, format='%Y%m%d-%H%M%S%f')
    
    log = PingViewerLogReader(str(input_path))

    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = [
            "real_time", "timestamp_offset", "message_id", "distance", "confidence",
            "transmit_duration", "ping_number", "scan_start", "scan_length",
            "gain_setting", "profile_data_length"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Process each decoded message filtering for Ping1D messages (message ID 1300)
        for timestamp, decoded_message in log.parser({1300}):
            if decoded_message.message_id == 1300:
                offset = parse_timestamp(timestamp)
                real_time = base_time + offset
                writer.writerow({
                    "real_time": real_time,
                    "timestamp_offset": timestamp.replace('\x00', ''),
                    "message_id": decoded_message.message_id,
                    "distance": getattr(decoded_message, "distance", ""),
                    "confidence": getattr(decoded_message, "confidence", ""),
                    "transmit_duration": getattr(decoded_message, "transmit_duration", ""),
                    "ping_number": getattr(decoded_message, "ping_number", ""),
                    "scan_start": getattr(decoded_message, "scan_start", ""),
                    "scan_length": getattr(decoded_message, "scan_length", ""),
                    "gain_setting": getattr(decoded_message, "gain_setting", ""),
                    "profile_data_length": getattr(decoded_message, "profile_data_length", "")
                })

    print(f"Decoded data saved to {output_csv}")

if __name__ == "__main__":
    main()
