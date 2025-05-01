import os
import argparse

def find_device_drive():
    for drive in range(65, 91):
        drive_letter = chr(drive) + ":\\"
        if os.path.exists(drive_letter + "APPS"):
            return drive_letter
        if os.path.exists(drive_letter + "conf_apps.cfg"):
            return drive_letter
    return None

def get_game_name_from_cfg(config_file):
    game_name = None
    with open(config_file, 'r') as file:
        config_lines = file.readlines()
        for line in config_lines:
            line = line.strip()
            if line.startswith("title="):
                game_name = line.split('=')[1]
            elif '=' in line:
                game_name = line.split('=')[0]
            if game_name:
                break
    return game_name

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--directory", 
    type=str, 
    required=True, 
    help="Path to the directory containing VCD files."
)

args = parser.parse_args()
vcd_directory = args.directory

game_vcd_tracker = {}

device_drive = find_device_drive()

if not device_drive:
    print("No device drive containing 'APPS' folder found.")
    exit()

config_file = None
game_name = None

# Check for title.cfg first in APPS/GAMENAME/
for game_folder in os.listdir(os.path.join(device_drive, "APPS")):
    potential_config = os.path.join(device_drive, "APPS", game_folder, "title.cfg")
    if os.path.exists(potential_config):
        config_file = potential_config
        game_name = game_folder
        break

if not config_file:
    conf_apps_path = os.path.join(device_drive, "conf_apps.cfg")
    if os.path.exists(conf_apps_path):
        config_file = conf_apps_path

if not config_file:
    print("No configuration file (title.cfg or conf_apps.cfg) found.")
    exit()

if not game_name:
    if config_file == conf_apps_path:
        game_name = get_game_name_from_cfg(config_file)

if not game_name:
    print("No game name found in the configuration file.")
    exit()

print(f"Game Name: {game_name}")

with open(config_file, 'r') as file:
    config_lines = file.readlines()

    boot_file = None
    for line in config_lines:
        line = line.strip()
        if line.startswith("title="):
            game_name = line.split('=')[1]
        elif line.startswith("boot="):
            boot_file = line.split('=')[1]

    if not boot_file:
        print(f"Boot file not found for {game_name} in {config_file}.")
        exit()

    if boot_file.startswith("XX."):
        vcd_filename = boot_file[3:].replace('.ELF', '.VCD')
    else:
        vcd_filename = boot_file.replace('.ELF', '.VCD')

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
