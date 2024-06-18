'''Checks if the user has the required python packages and launches if true.'''

import os
import importlib
import sys

from pathlib import Path

#Required Packages to run the script, ask user to install if not present
rp = ['PyQt6','numpy','xlsxwriter','git','requests']
for package in rp:
    try: globals()[package] = importlib.import_module(package)
    except (ModuleNotFoundError,ImportError) as e:
        #If user does not have git in their user path on windows
        if str(e).split()[0] == 'Failed':
            #First check if git is even installed
            root = Path(f"{os.path.dirname(os.getenv('APPDATA'))}/Local")
            git_exe_root = Path(f'{root}/GitHubDesktop')
            if os.path.isdir(git_exe_root) == False:
                print('Gitdesktop not detected on system, please install from provided url:')
                print('https://desktop.github.com/')
                sys.exit()
            #If git is installed search folder for exe
            exe_location = str(list(Path(git_exe_root).rglob("git.exe"))[0])
            exe_location = os.path.dirname(exe_location)
            #Add exe to the path such that gui can be loaded
            my_env = os.environ
            my_env['PATH'] = exe_location+';'+my_env['PATH']
        else:
            print(f'{package} cannot be found, would you like to install it (y/n)?')
            answer = input()
            if answer == 'y':
                #gitpython imports as git, annoying I know
                if package == 'git':
                    package = 'gitpython'
                os.system(f'pip install {package}')

#If user can load all libraries load GUI
from Launch.Launch_PyQt import main
main()
