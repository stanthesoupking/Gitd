"""Install or uninstall Gitd
"""

from sys import argv, stderr
from io import FileIO
from os import getcwd, chmod, mkdir, path, remove
import subprocess
import platform
from pathlib import Path

# Get current platform
current_platform = platform.system()

# If platform isn't Linux
if current_platform != 'Linux':
    # Display warning and ask user if they still want to proceed

    print(f"Warning: this installer is not supported by {current_platform} " +
        "and may break your computer.")

    ans = None
    while(ans is None):
        ans = input("Would you still like to continue (y/n)? ")
        if(ans == 'y'):
            ans = True
        elif(ans == 'n'):
            exit()
        else:
            print('Invalid input')
            ans = None
    

# Path to install executable
INSTALL_FOLDER = path.join(str(Path.home()), "bin")
LAUNCHER_NAME = "gitd"

launcher_path = path.join(INSTALL_FOLDER, LAUNCHER_NAME)

def source_profile():
    """Sources the '~/.profile' file to update binaries inside the user's
    private ~/bin folder
    """
    if(path.isfile('~/.profile')):
        subprocess.run(["source", "~/.profile"])

if(len(argv) < 2):
    print("Error: You must supply a command to execute, try running 'help' for " +
        "a list of the available commands.", file = stderr)
else:
    command = argv[1]
    if(command == 'help'):
        # List available commands
        print("Available commands are:\n"+
            "help\tinstall\tuninstall")
    elif(command == 'install'):
        print("Attempting to install...")
        
        # Check if the current user's bin directory exists
        exists = path.isdir(INSTALL_FOLDER)

        # Create directory if it doesn't exist
        if not exists:
            mkdir(INSTALL_FOLDER)

        # Create launcher file
        try:
            file = FileIO(launcher_path, "wb")
        except PermissionError:
            print("Error: Insufficient permissions.")
            exit()

        run_command = 'python3 ' + getcwd() + '/main.py $1 $2 $3\n'
        file.write('#!/bin/bash\n'.encode())
        file.write(run_command.encode())
        file.close()

        # Make launcher executable
        chmod(launcher_path, 0o777)

        # Try sourcing the .profile file if it exists
        source_profile()

        print("Installation complete!")
        print("Tip: You can uninstall Gitd by running this file with the 'uninstall' " +
            "argument")
    elif(command == 'uninstall'):
        print('Attempting to uninstall...')

        if not path.isfile(launcher_path):
            print("Gitd isn't installed.")
            exit()

        try:
            remove(launcher_path)
        except:
            print(f"Error: failed deleting '{launcher_path}'. Check your " +
                "permissions and try again.")

        source_profile()

        print("Gitd uninstalled.")