import os
import sys
import shlex
import shutil
import subprocess
import platform
import getpass
import time
from pathlib import Path

import colorama
from colorama import Fore, Style

# ---------------------------------------------------------
# Initialization
# ---------------------------------------------------------

colorama.init(autoreset=True)

SHELL_NAME = "IIUI-Shell"
VERSION = "2.0.0"
AUTHOR = "Amna"

HISTORY_FILE = Path.home() / ".iiui_shell_history"

IS_WINDOWS = os.name == "nt"


# ---------------------------------------------------------
# Optional readline support
# ---------------------------------------------------------

try:
    if IS_WINDOWS:
        import readline
    else:
        import readline

    READLINE_AVAILABLE = True

except ImportError:
    READLINE_AVAILABLE = False


# ---------------------------------------------------------
# History
# ---------------------------------------------------------

def load_history():
    """Load previous commands from history file."""

    if not READLINE_AVAILABLE:
        return

    try:
        if HISTORY_FILE.exists():
            readline.read_history_file(str(HISTORY_FILE))

    except Exception:
        pass


def save_history():
    """Save shell history."""

    if not READLINE_AVAILABLE:
        return

    try:
        readline.write_history_file(str(HISTORY_FILE))

    except Exception:
        pass


# ---------------------------------------------------------
# Tab Completion
# ---------------------------------------------------------

COMMANDS = [
    "cd",
    "pwd",
    "ls",
    "dir",
    "mkdir",
    "rmdir",
    "rm",
    "del",
    "touch",
    "cat",
    "type",
    "echo",
    "clear",
    "cls",
    "history",
    "help",
    "about",
    "exit",
    "quit",
    "whoami",
    "which",
    "where",
    "date",
    "tree",
]


def setup_completion():
    """Enable command and filename completion."""

    if not READLINE_AVAILABLE:
        return

    def completer(text, state):

        buffer = readline.get_line_buffer()

        # Complete commands
        if not buffer.strip() or (
            " " not in buffer and "\t" not in buffer
        ):
            options = [
                command
                for command in COMMANDS
                if command.startswith(text)
            ]

            try:
                return options[state]
            except IndexError:
                return None

        # Complete filesystem paths
        directory = os.path.dirname(text) or "."
        filename = os.path.basename(text)

        try:
            entries = os.listdir(directory)
        except OSError:
            entries = []

        matches = [
            entry
            for entry in entries
            if entry.startswith(filename)
        ]

        try:
            match = matches[state]

            full_path = os.path.join(directory, match)

            if os.path.isdir(full_path):
                match += os.sep

            if directory != ".":
                return os.path.join(directory, match)

            return match

        except IndexError:
            return None

    readline.set_completer(completer)

    try:
        readline.parse_and_bind("tab: complete")
    except Exception:
        pass


# ---------------------------------------------------------
# Colors / UI
# ---------------------------------------------------------

def success(message):
    print(Fore.GREEN + message)


def error(message):
    print(Fore.RED + message)


def warning(message):
    print(Fore.YELLOW + message)


def info(message):
    print(Fore.CYAN + message)


def print_separator():
    print(Fore.GREEN + "─" * 70)


# ---------------------------------------------------------
# Banner
# ---------------------------------------------------------

def print_header():
    print()

    print(Fore.CYAN + r"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                    🐚  IIUI MINI SHELL                              ║
║                                                                      ║
║             Advanced Python Command-Line Environment                ║
║                                                                      ║
║        Version 2.0.0  •  Cross-Platform  •  Python                  ║
║                                                                      ║
║                 Type 'help' to get started                           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    print(
        Fore.YELLOW
        + "                  Welcome to IIUI Shell!"
    )

    print_separator()

    print(
        Fore.WHITE
        + f"  Version : {VERSION}"
    )

    print(
        Fore.WHITE
        + f"  Author  : {AUTHOR}"
    )

    print(
        Fore.WHITE
        + f"  System  : {platform.system()} {platform.release()}"
    )

    print(
        Fore.WHITE
        + "  Type 'help' to explore available commands."
    )

    print_separator()
    print()

# ---------------------------------------------------------
# Prompt
# ---------------------------------------------------------

def get_prompt():

    current_directory = os.getcwd()

    home = str(Path.home())

    if current_directory.startswith(home):
        current_directory = "~" + current_directory[len(home):]

    username = getpass.getuser()

    return (
        Fore.MAGENTA
        + username
        + Fore.WHITE
        + "@"
        + Fore.CYAN
        + "IIUI"
        + Fore.WHITE
        + ":"
        + Fore.BLUE
        + current_directory
        + Fore.YELLOW
        + "\n❯ "
        + Style.RESET_ALL
    )


# ---------------------------------------------------------
# Built-in: CD
# ---------------------------------------------------------

def command_cd(args):

    if not args:
        target = str(Path.home())
    else:
        target = os.path.expanduser(args[0])

    try:
        os.chdir(target)

    except FileNotFoundError:
        error(f"cd: directory not found: {target}")

    except NotADirectoryError:
        error(f"cd: not a directory: {target}")

    except PermissionError:
        error(f"cd: permission denied: {target}")


# ---------------------------------------------------------
# Built-in: PWD
# ---------------------------------------------------------

def command_pwd():

    print(os.getcwd())


# ---------------------------------------------------------
# Built-in: MKDIR
# ---------------------------------------------------------

def command_mkdir(args):

    if not args:
        error("mkdir: missing operand")
        return

    for directory in args:

        try:
            Path(directory).mkdir(parents=True, exist_ok=False)
            success(f"Created directory: {directory}")

        except FileExistsError:
            error(f"mkdir: already exists: {directory}")

        except PermissionError:
            error(f"mkdir: permission denied: {directory}")


# ---------------------------------------------------------
# Built-in: RMDIR
# ---------------------------------------------------------

def command_rmdir(args):

    if not args:
        error("rmdir: missing operand")
        return

    for directory in args:

        try:
            Path(directory).rmdir()
            success(f"Removed directory: {directory}")

        except FileNotFoundError:
            error(f"rmdir: directory not found: {directory}")

        except OSError:
            error(
                f"rmdir: directory is not empty or cannot be removed: "
                f"{directory}"
            )


# ---------------------------------------------------------
# Built-in: TOUCH
# ---------------------------------------------------------

def command_touch(args):

    if not args:
        error("touch: missing file operand")
        return

    for filename in args:

        try:
            Path(filename).touch(exist_ok=True)
            success(f"Touched: {filename}")

        except PermissionError:
            error(f"touch: permission denied: {filename}")


# ---------------------------------------------------------
# Built-in: RM
# ---------------------------------------------------------

def command_rm(args):

    if not args:
        error("rm: missing operand")
        return

    for target in args:

        path = Path(target)

        if not path.exists():
            error(f"rm: cannot find: {target}")
            continue

        try:

            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

            success(f"Removed: {target}")

        except PermissionError:
            error(f"rm: permission denied: {target}")

        except Exception as exc:
            error(f"rm: {exc}")


# ---------------------------------------------------------
# Built-in: CAT / TYPE
# ---------------------------------------------------------

def command_cat(args):

    if not args:
        error("cat: missing file operand")
        return

    for filename in args:

        try:

            with open(filename, "r", encoding="utf-8") as file:
                print(file.read(), end="")

        except FileNotFoundError:
            error(f"cat: file not found: {filename}")

        except UnicodeDecodeError:
            error(f"cat: cannot read binary file: {filename}")

        except PermissionError:
            error(f"cat: permission denied: {filename}")


# ---------------------------------------------------------
# Built-in: ECHO
# ---------------------------------------------------------

def command_echo(args):

    print(" ".join(args))


# ---------------------------------------------------------
# Built-in: CLEAR
# ---------------------------------------------------------

def command_clear():

    os.system("cls" if IS_WINDOWS else "clear")


# ---------------------------------------------------------
# Built-in: HISTORY
# ---------------------------------------------------------

def command_history():

    if not READLINE_AVAILABLE:
        warning("Command history is unavailable on this system.")
        return

    try:

        history_length = readline.get_current_history_length()

        if history_length == 0:
            info("No commands in history.")
            return

        for index in range(1, history_length + 1):

            command = readline.get_history_item(index)

            if command:
                print(
                    Fore.YELLOW
                    + f"{index:4}"
                    + Fore.WHITE
                    + f"  {command}"
                )

    except Exception as exc:
        error(f"history: {exc}")


# ---------------------------------------------------------
# Built-in: WHOAMI
# ---------------------------------------------------------

def command_whoami():

    print(getpass.getuser())


# ---------------------------------------------------------
# Built-in: WHICH / WHERE
# ---------------------------------------------------------

def command_which(args):

    if not args:
        error("which: missing command")
        return

    for command in args:

        location = shutil.which(command)

        if location:
            print(location)
        else:
            error(f"{command}: command not found")


# ---------------------------------------------------------
# Built-in: DATE
# ---------------------------------------------------------

def command_date():

    print(time.strftime("%A, %d %B %Y %H:%M:%S"))


# ---------------------------------------------------------
# Built-in: TREE
# ---------------------------------------------------------

def command_tree(args):

    root = Path(args[0]) if args else Path(".")

    if not root.exists():
        error(f"tree: path not found: {root}")
        return

    print(root)

    def walk(directory, prefix=""):

        try:
            entries = sorted(
                directory.iterdir(),
                key=lambda path: (not path.is_dir(), path.name.lower())
            )
        except PermissionError:
            error(f"tree: permission denied: {directory}")
            return

        for index, entry in enumerate(entries):

            connector = "└── " if index == len(entries) - 1 else "├── "

            print(prefix + connector + entry.name)

            if entry.is_dir():

                extension = "    " if index == len(entries) - 1 else "│   "

                walk(
                    entry,
                    prefix + extension
                )

    walk(root)


# ---------------------------------------------------------
# HELP
# ---------------------------------------------------------

def command_help():

    print()

    print(Fore.CYAN + "IIUI Mini Shell — Command Reference")
    print_separator()

    commands = {

        "cd <dir>": "Change the current directory",
        "pwd": "Print the current directory",

        "ls / dir": "List files and directories",

        "mkdir <dir>": "Create a directory",
        "rmdir <dir>": "Remove an empty directory",

        "touch <file>": "Create an empty file",
        "rm <file>": "Remove a file or directory",

        "cat <file>": "Display file contents",
        "echo <text>": "Print text",

        "clear / cls": "Clear the terminal",
        "history": "Show command history",

        "whoami": "Display current username",
        "which <cmd>": "Locate an executable",

        "date": "Display current date and time",
        "tree": "Display directory tree",

        "about": "Display shell information",
        "help": "Display this help message",
        "exit / quit": "Exit IIUI Mini Shell",
    }

    for command, description in commands.items():

        print(
            Fore.YELLOW
            + f"  {command:<20}"
            + Fore.WHITE
            + description
        )

    print()

    print(Fore.CYAN + "Shell Features")
    print_separator()

    features = [
        "Command history",
        "Arrow-key navigation",
        "Tab auto-completion",
        "Pipes: command1 | command2",
        "Output redirection: command > file",
        "Append redirection: command >> file",
        "Input redirection: command < file",
        "Background execution: command &",
        "Windows / Linux / macOS support",
    ]

    for feature in features:
        print(Fore.GREEN + "  ✓ " + Fore.WHITE + feature)

    print()


# ---------------------------------------------------------
# ABOUT
# ---------------------------------------------------------

def command_about():

    print()

    print(Fore.MAGENTA + "╭" + "─" * 58 + "╮")

    print(
        Fore.MAGENTA
        + "│"
        + Fore.WHITE
        + "              IIUI MINI SHELL v2.0"
        + " " * 24
        + Fore.MAGENTA
        + "│"
    )

    print(
        Fore.MAGENTA
        + "│"
        + Fore.WHITE
        + "  A custom command-line shell built with Python."
        + " " * 10
        + Fore.MAGENTA
        + "│"
    )

    print(
        Fore.MAGENTA
        + "│"
        + Fore.WHITE
        + "  Features: history, completion, pipes,"
        + " " * 17
        + Fore.MAGENTA
        + "│"
    )

    print(
        Fore.MAGENTA
        + "│"
        + Fore.WHITE
        + "  redirection, background processes & more."
        + " " * 13
        + Fore.MAGENTA
        + "│"
    )

    print(
        Fore.MAGENTA
        + "│"
        + Fore.WHITE
        + f"  Platform: {platform.system()}"
        + " " * (58 - len(platform.system()) - 12)
        + Fore.MAGENTA
        + "│"
    )

    print(
        Fore.MAGENTA
        + "│"
        + Fore.WHITE
        + f"  Python: {platform.python_version()}"
        + " " * (58 - len(platform.python_version()) - 11)
        + Fore.MAGENTA
        + "│"
    )

    print(
        Fore.MAGENTA
        + "╰"
        + "─" * 58
        + "╯"
    )

    print()


# ---------------------------------------------------------
# Built-in dispatcher
# ---------------------------------------------------------

def handle_builtin(cmd_parts):

    if not cmd_parts:
        return True

    command = cmd_parts[0].lower()
    args = cmd_parts[1:]

    if command == "cd":
        command_cd(args)

    elif command == "pwd":
        command_pwd()

    elif command in ("mkdir",):
        command_mkdir(args)

    elif command in ("rmdir",):
        command_rmdir(args)

    elif command == "touch":
        command_touch(args)

    elif command in ("rm", "del"):
        command_rm(args)

    elif command in ("cat", "type"):
        command_cat(args)

    elif command == "echo":
        command_echo(args)

    elif command in ("clear", "cls"):
        command_clear()

    elif command == "history":
        command_history()

    elif command == "whoami":
        command_whoami()

    elif command in ("which", "where"):
        command_which(args)

    elif command == "date":
        command_date()

    elif command == "tree":
        command_tree(args)

    elif command == "help":
        command_help()

    elif command == "about":
        command_about()

    elif command in ("exit", "quit"):

        save_history()

        print()
        print(Fore.YELLOW + "Goodbye from IIUI Mini Shell! 👋")
        print()

        sys.exit(0)

    else:
        return False

    return True


# ---------------------------------------------------------
# Command normalization
# ---------------------------------------------------------

WINDOWS_ALIASES = {
    "ls": "dir",
}


def normalize_command(command):

    if IS_WINDOWS:

        first_word = command.split(maxsplit=1)[0].lower()

        if first_word in WINDOWS_ALIASES:

            replacement = WINDOWS_ALIASES[first_word]

            return replacement + command[len(first_word):]

    return command


# ---------------------------------------------------------
# Redirection Parser
# ---------------------------------------------------------

def parse_redirection(command):

    input_file = None
    output_file = None
    append_output = False

    if ">>" in command:

        command, output_file = command.split(">>", 1)

        output_file = output_file.strip()
        append_output = True

    elif ">" in command:

        command, output_file = command.split(">", 1)

        output_file = output_file.strip()

    if "<" in command:

        command, input_file = command.split("<", 1)

        input_file = input_file.strip()

    return (
        command.strip(),
        input_file,
        output_file,
        append_output,
    )


# ---------------------------------------------------------
# External command execution
# ---------------------------------------------------------

def execute_external(command):

    command = normalize_command(command)

    command, input_file, output_file, append_output = (
        parse_redirection(command)
    )

    background = False

    if command.endswith("&"):

        background = True
        command = command[:-1].strip()

    if not command:
        return

    # -----------------------------------------------------
    # PIPE SUPPORT
    # -----------------------------------------------------

    if "|" in command:

        pipeline_commands = [
            part.strip()
            for part in command.split("|")
        ]

        processes = []
        previous_stdout = None

        opened_input = None
        opened_output = None

        try:

            if input_file:
                opened_input = open(
                    input_file,
                    "r",
                    encoding="utf-8"
                )

            for index, part in enumerate(pipeline_commands):

                args = shlex.split(
                    part,
                    posix=not IS_WINDOWS
                )

                if not args:
                    continue

                is_last = index == len(pipeline_commands) - 1

                stdin = (
                    previous_stdout
                    if previous_stdout
                    else opened_input
                )

                stdout = subprocess.PIPE

                if is_last:

                    if output_file:

                        mode = "a" if append_output else "w"

                        opened_output = open(
                            output_file,
                            mode,
                            encoding="utf-8"
                        )

                        stdout = opened_output

                    else:
                        stdout = None

                process = subprocess.Popen(
                    args,
                    stdin=stdin,
                    stdout=stdout,
                    stderr=None,
                    shell=False
                )

                processes.append(process)

                if previous_stdout:
                    previous_stdout.close()

                previous_stdout = process.stdout

            if background:

                info(
                    f"Started pipeline in background "
                    f"(PID {processes[-1].pid})"
                )

            else:

                for process in processes:
                    process.wait()

        except FileNotFoundError:

            error(
                f"Command not found: "
                f"{pipeline_commands[0].split()[0]}"
            )

        except PermissionError:

            error("Permission denied.")

        except Exception as exc:

            error(f"Pipeline error: {exc}")

        finally:

            if opened_input:
                opened_input.close()

            if opened_output:
                opened_output.close()

        return

    # -----------------------------------------------------
    # NORMAL COMMAND
    # -----------------------------------------------------

    try:

        args = shlex.split(
            command,
            posix=not IS_WINDOWS
        )

        if not args:
            return

        stdin = None
        stdout = None

        if input_file:

            stdin = open(
                input_file,
                "r",
                encoding="utf-8"
            )

        if output_file:

            mode = "a" if append_output else "w"

            stdout = open(
                output_file,
                mode,
                encoding="utf-8"
            )

        start_time = time.perf_counter()

        if IS_WINDOWS:

            # Windows built-in commands such as
            # ipconfig, set, ver, etc.
            executable = shutil.which(args[0])

            if executable:

                process_command = args

                if background:

                    process = subprocess.Popen(
                        process_command,
                        stdin=stdin,
                        stdout=stdout
                    )

                    info(
                        f"Process started in background "
                        f"(PID {process.pid})"
                    )

                else:

                    subprocess.run(
                        process_command,
                        stdin=stdin,
                        stdout=stdout
                    )

            else:

                # Fall back to Windows command processor
                process_command = command

                if background:

                    process = subprocess.Popen(
                        process_command,
                        stdin=stdin,
                        stdout=stdout,
                        shell=True
                    )

                    info(
                        f"Process started in background "
                        f"(PID {process.pid})"
                    )

                else:

                    subprocess.run(
                        process_command,
                        stdin=stdin,
                        stdout=stdout,
                        shell=True
                    )

        else:

            if background:

                process = subprocess.Popen(
                    args,
                    stdin=stdin,
                    stdout=stdout
                )

                info(
                    f"Process started in background "
                    f"(PID {process.pid})"
                )

            else:

                subprocess.run(
                    args,
                    stdin=stdin,
                    stdout=stdout
                )

        elapsed = time.perf_counter() - start_time

        if not background and elapsed >= 0.5:

            print(
                Fore.BLACK
                + f"[completed in {elapsed:.2f}s]"
                + Style.RESET_ALL
            )

    except FileNotFoundError:

        error(
            f"{args[0]}: command not found"
        )

    except PermissionError:

        error(
            f"{args[0]}: permission denied"
        )

    except Exception as exc:

        error(
            f"Execution error: {exc}"
        )

    finally:

        if stdin:
            stdin.close()

        if stdout:
            stdout.close()


# ---------------------------------------------------------
# Main Shell
# ---------------------------------------------------------

def iiui_shell():

    load_history()
    setup_completion()

    print_header()

    while True:

        try:

            command_input = input(
                get_prompt()
            ).strip()

            if not command_input:
                continue

            # Add command to history
            if READLINE_AVAILABLE:

                try:
                    readline.add_history(command_input)
                except Exception:
                    pass

            # Parse first command for built-ins
            try:

                parsed = shlex.split(
                    command_input,
                    posix=not IS_WINDOWS
                )

            except ValueError as exc:

                error(f"Syntax error: {exc}")
                continue

            if not parsed:
                continue

            # Built-in commands
            if handle_builtin(parsed):
                continue

            # External commands
            execute_external(command_input)

        except KeyboardInterrupt:

            print()
            warning(
                "Keyboard interrupt. "
                "Type 'exit' to quit."
            )

        except EOFError:

            print()
            save_history()

            print(
                Fore.YELLOW
                + "Goodbye from IIUI Mini Shell! 👋"
            )

            break

        except Exception as exc:

            error(f"Shell error: {exc}")


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":

    try:
        iiui_shell()

    except KeyboardInterrupt:

        save_history()

        print(
            Fore.YELLOW
            + "\nGoodbye from IIUI Mini Shell! 👋"
        )