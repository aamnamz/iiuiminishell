import os
import subprocess
import shlex
import readline  # Enables history and tab completion
import time
from colorama import Fore, Style, init

init(autoreset=True)

HISTORY_FILE = os.path.expanduser("~/.iiui_shell_history")

# Load command history
if os.path.exists(HISTORY_FILE):
    readline.read_history_file(HISTORY_FILE)

# Enable tab completion for filenames
readline.parse_and_bind("tab: complete")

# Welcome Banner
def print_header():
    print(Fore.GREEN + "=" * 60)
    print(Fore.YELLOW + "🖥️  IIUI Mini Shell — Advanced Edition")
    print(Fore.GREEN + "Created with ❤️  by [Your Name] | Type 'help' for info")
    print("=" * 60 + Style.RESET_ALL)

# Handle built-in commands
def handle_builtins(cmd_parts):
    cmd = cmd_parts[0]
    if cmd == "cd":
        if len(cmd_parts) > 1:
            try:
                os.chdir(cmd_parts[1])
            except FileNotFoundError:
                print(Fore.RED + f"No such directory: {cmd_parts[1]}")
        else:
            print("cd: missing operand")
        return True

    elif cmd == "exit":
        print(Fore.YELLOW + "Exiting IIUI-Shell. Goodbye!")
        readline.write_history_file(HISTORY_FILE)
        exit(0)

    elif cmd == "help":
        print(Fore.CYAN + """
Supported Features:
- Standard commands: ls, pwd, echo, mkdir, rm, etc.
- cd: Change directory
- exit: Exit shell
- | : Pipe output between commands
- >, < : Redirect output/input
- & : Run process in background
- help, clear, about: Built-in shell commands
        """)
        return True

    elif cmd == "clear":
        os.system("cls" if os.name == "nt" else "clear")
        return True

    elif cmd == "about":
        print(Fore.MAGENTA + "IIUI Mini Shell v1.0 — Developed by [Your Name]\nAdvanced Shell Simulation Project for OS Course")
        return True

    return False

# Execute external commands with optional piping and redirection
def execute_command(cmd_input):
    background = False
    if cmd_input.endswith('&'):
        background = True
        cmd_input = cmd_input[:-1].strip()

    # I/O Redirection Handling
    input_file = None
    output_file = None

    if '>' in cmd_input:
        parts = cmd_input.split('>')
        cmd_input = parts[0].strip()
        output_file = parts[1].strip()

    if '<' in cmd_input:
        parts = cmd_input.split('<')
        cmd_input = parts[0].strip()
        input_file = parts[1].strip()

    # Pipe Handling
    if '|' in cmd_input:
        cmds = [shlex.split(c.strip()) for c in cmd_input.split('|')]
        prev = None
        for i, cmd in enumerate(cmds):
            stdin = prev.stdout if prev else (open(input_file, 'r') if input_file and i == 0 else None)
            stdout = subprocess.PIPE if i < len(cmds) - 1 else (open(output_file, 'w') if output_file else None)
            prev = subprocess.Popen(cmd, stdin=stdin, stdout=stdout)
            if stdin: stdin.close()
        if not background:
            prev.communicate()
    else:
        cmd_parts = shlex.split(cmd_input)
        stdin = open(input_file, 'r') if input_file else None
        stdout = open(output_file, 'w') if output_file else None

        if background:
            subprocess.Popen(cmd_parts, stdin=stdin, stdout=stdout)
        else:
            subprocess.run(cmd_parts, stdin=stdin, stdout=stdout)

        if stdin: stdin.close()
        if stdout: stdout.close()

# Main shell loop
def iiui_shell():
    print_header()
    while True:
        try:
            cmd_input = input(Fore.CYAN + "IIUI-Shell> " + Style.RESET_ALL).strip()
            if not cmd_input:
                continue

            if handle_builtins(shlex.split(cmd_input)):
                continue

            execute_command(cmd_input)

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except Exception as e:
            print(Fore.RED + f"Error: {e}")

if __name__ == "__main__":
    iiui_shell()