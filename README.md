# 🐚 IIUI Mini Shell

A custom command-line shell built in Python with history, auto-completion, and cross-platform support.

## ✨ Features
- **10+ Built-in Commands**: `cd`, `pwd`, `help`, `exit`, `about`, etc.
- **Command History**: Navigate previous commands with arrow keys
- **Tab Auto-completion**: Press Tab to complete commands
- **Cross-platform**: Handles Windows/Unix command differences
- **Standalone .exe**: Compiled with PyInstaller for easy distribution

## 🚀 Quick Start

# Install dependencies
pip install pyreadline3 pyinstaller

# Run the shell
python shell.py

# Or use compiled version (Windows)
./dist/shell.exe
📦 Compilation
bash
pyinstaller --onefile --hidden-import=pyreadline3 shell.py
🛠️ Built With
Python 3

pyreadline3 (for Windows compatibility)

PyInstaller

📝 Project Info
Course: Operating Systems

University: IIUI

Year: 2024
