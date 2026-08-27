# 🐚 IIUI Mini Shell

A lightweight, cross-platform command-line shell built with Python, featuring persistent command history, Tab auto-completion, built-in filesystem commands, pipes, I/O redirection, background process execution, and a standalone Windows executable.

## ✨ Features

- **20+ Built-in Commands**
  - `cd` — Change directory
  - `pwd` — Show current directory
  - `ls` / `dir` — List files and directories
  - `mkdir` — Create directories
  - `rmdir` — Remove empty directories
  - `touch` — Create files
  - `rm` / `del` — Remove files or directories
  - `cat` / `type` — Display file contents
  - `echo` — Print text
  - `clear` / `cls` — Clear terminal
  - `history` — View command history
  - `whoami` — Display current username
  - `which` / `where` — Locate commands
  - `date` — Display current date and time
  - `tree` — Display directory structure
  - `help` — Show command reference
  - `about` — Display shell information
  - `exit` / `quit` — Exit the shell

- **Command History**
  - Persistent history saved between sessions
  - Navigate previous commands with arrow keys

- **Tab Auto-completion**
  - Complete commands using `Tab`
  - Complete files and directories

- **Pipes**
  ```bash
  command1 | command2
