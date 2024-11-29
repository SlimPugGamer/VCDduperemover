import os
import argparse

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

args = parser.parse_args()
vcd_directory = args.directory
config_file = args.config

game_vcd_tracker = {}

if not os.path.exists(config_file):
    print(f"Configuration file {config_file} not found.")
    exit()

with open(config_file, 'r') as file:
    for line in file:
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

        vcd_path = os.path.join(vcd_directory, vcd_filename)

        if os.path.exists(vcd_path):
            print(f"Found VCD file for {game_name}: {vcd_filename}")
            file_size = os.path.getsize(vcd_path)

            if file_size == 0:
                print(f"Warning: {vcd_filename} is empty.")
                user_input = input(f"Do you want to delete the empty VCD file {vcd_filename}? (y/n): ")
                if user_input.lower() == 'y':
                    try:
                        os.remove(vcd_path)
                        print(f"Deleted {vcd_filename}")
                    except FileNotFoundError:
                        print(f"{vcd_filename} not found, possibly already deleted.")
            else:
                print(f"{vcd_filename} size is {file_size} bytes.")


                if game_name in game_vcd_tracker:
                    existing_vcd_path = game_vcd_tracker[game_name]
                    existing_file_size = os.path.getsize(existing_vcd_path)

                    if file_size == existing_file_size:
                        print(f"Warning: {vcd_filename} is the same size as the existing VCD for {game_name}.")
                        user_input = input(f"Do you want to delete the duplicate VCD file {vcd_filename}? (y/n): ")
                        if user_input.lower() == 'y':
                            try:
                                os.remove(vcd_path)
                                print(f"Deleted duplicate {vcd_filename}")
                            except FileNotFoundError:
                                print(f"{vcd_filename} not found, possibly already deleted.")
                else:
                    game_vcd_tracker[game_name] = vcd_path

        else:
            print(f"Missing VCD file for {game_name}: {vcd_filename}")
