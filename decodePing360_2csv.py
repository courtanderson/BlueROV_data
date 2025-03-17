    #!/usr/bin/env python3
import numpy as np
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
        description="Decode Ping360 binary file and output sonar data to CSV with real timestamps"
    )
    parser.add_argument("file", help="Input binary file containing Ping360 data")
    parser.add_argument("-o", "--output", default="output.csv",
                        help="Output CSV file (default: output.csv)")
    args = parser.parse_args()

    # Calculate the base time from the file's stem.
    # For example, a file named "20250306-115328280.bin" represents the base time.
    base_time = pd.to_datetime(Path(args.file).stem, format='%Y%m%d-%H%M%S%f')
    
    log = PingViewerLogReader(args.file)

    # Open CSV file for writing
    with open(args.output, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write CSV header
        writer.writerow(["real_time", "timestamp_offset", "angle_deg", "sample_index", "distance_m", "intensity"])
        
        # Iterate over only Ping360 device_data messages (message ID 2300)
        for timestamp, decoded_message in log.parser({2300}):
            # Compute the real timestamp by adding the offset (from the message) to the base time.
            offset = parse_timestamp(timestamp)
            real_time = base_time + offset

            # Convert angle from gradians to degrees (1 gradian = 0.9 degree)
            angle_deg = decoded_message.angle * 0.9

            # Convert the raw intensity data into a NumPy array.
            intensities = np.frombuffer(decoded_message.data, dtype=np.uint8)
            
            # Calculate distance per sample:
            # sample_period is in increments of 25 ns.
            # The time for each sample is: sample_period * 25e-9 seconds.
            # Since the pulse makes a round trip, distance = (speed_of_sound * t_sample) / 2.
            speed_of_sound = 1500.0  # in m/s
            t_sample = decoded_message.sample_period * 25e-9  # seconds
            distance_per_sample = (speed_of_sound * t_sample) / 2.0

            # Write one CSV row per sample.
            for i, intensity in enumerate(intensities):
                distance = i * distance_per_sample
                writer.writerow([real_time, timestamp.replace('\x00', ''), angle_deg, i, distance, intensity])

if __name__ == "__main__":
    main()

