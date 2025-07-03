import sys
import shutil
import time
import platform
import os

RED = "\033[91m"
WHITE = "\033[97m"
RESET = "\033[0m"
CURSOR_BLOCK = "\u2588"
TEXT = "baybay"

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

def move_cursor(row, col):
    # ANSI escape code for moving cursor (works on most terminals)
    sys.stdout.write(f"\033[{row};{col}H")
    sys.stdout.flush()

def loader(duration=3):
    size = shutil.get_terminal_size()
    width, height = size.columns, size.lines
    center_line = max(1, height // 2)
    center_col = max(1, (width - len(TEXT) - 2) // 2)  # -2 for space and cursor

    clear_screen()
    start = time.time()
    visible = True

    try:
        while time.time() - start < duration:
            move_cursor(center_line, center_col)
            sys.stdout.write(WHITE + TEXT + RESET + " ")
            cursor = f"{RED}{CURSOR_BLOCK}{RESET}" if visible else " "
            sys.stdout.write(cursor)
            sys.stdout.flush()
            visible = not visible
            time.sleep(0.5)
            # Clear line after each frame
            move_cursor(center_line, center_col)
            sys.stdout.write(" " * (len(TEXT) + 2))
            sys.stdout.flush()
    finally:
        clear_screen()
        move_cursor(0, 0)
        sys.stdout.flush()