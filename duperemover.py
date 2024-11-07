import os
import argparse

# Set up command-line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--directory", 
    type=str, 
    required=True, 
    help="Path to the directory containing VCD files."
)
parser.add_argument(
    "-c", "--config", 
    type=str, 
    required=True, 
    help="Path to the configuration file."
)

# Parse the arguments
args = parser.parse_args()
vcd_directory = args.directory
config_file = args.config

# Track duplicates for any VCD file based on game name
game_vcd_tracker = {}
# Check if the configuration file exists
if not os.path.exists(config_file):
    print(f"Configuration file {config_file} not found.")
    exit()

# Read the config file and process each line
with open(config_file, 'r') as file:
    for line in file:
        # fix for missing VCD as it was looking for the same name for the ELF and VCD
        try:
            game_name, file_path = line.strip().split('=')
            file_name = os.path.basename(file_path)

            if file_name.startswith('XX.'):
                vcd_filename = file_name[3:].replace('.ELF', '.VCD')
            else:
                vcd_filename = file_name.replace('.ELF', '.VCD')

        except ValueError:
            print(f"Skipping malformed line: {line.strip()}")
            continue

        # Full path to the VCD file
        vcd_path = os.path.join(vcd_directory, vcd_filename)

        # Check if the VCD file exists
        if os.path.exists(vcd_path):
            print(f"Found VCD file for {game_name}: {vcd_filename}")
        else:
            print(f"Missing VCD file for {game_name}: {vcd_filename}")

        # Track and handle duplicates for any game
        if game_name in game_vcd_tracker:
            # If duplicate found, delete it
            print(f"Deleting duplicate VCD file for {game_name}: {vcd_filename}")
            try:
                os.remove(vcd_path)
                print(f"Deleted {vcd_filename}")
            except FileNotFoundError:
                print(f"Duplicate VCD {vcd_filename} not found, possibly already deleted.")
        else:
            # First occurrence, add to tracker
            game_vcd_tracker[game_name] = vcd_path
