'''Checks if the user has the required python packages and launches if true.'''

import importlib
import os
import subprocess
import sys

from pathlib import Path

CWD = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(CWD, 'Scripts'))
sys.path.append(os.path.join(CWD, 'Icons'))
sys.path.append(os.path.join(CWD, 'Launch'))

#Required Packages to run the script, ask user to install if not present
rp = ['PyQt5','numpy','xlsxwriter','git']
for package in rp:
    try: globals()[package] = importlib.import_module(package)
    except (ModuleNotFoundError,ImportError) as e:
        #If user does not have git in their user path on windows
        if str(e).split()[0] == 'Failed':
            #First check if git is even installed
            root = os.getenv('APPDATA')
            git_exe_root = Path(f'{root}/GitHubDesktop')
            if os.path.isdir(git_exe_root) == False:
                print('Gitdesktop not detected on system, please install from provided url:')
                print('https://desktop.github.com/')
                sys.exit()
            #If git is installed search folder for exe
            exe_location = list(Path(git_exe_root).rglob("*.[e][x][e]"))
            #Add exe to the path and then launch a second instance
            my_env = os.environ
            my_env['PATH'] = exe_location+';'+my_env['PATH']
            subprocess.Popen('python '+os.getcwd()+'\\Launcher.py',env=my_env)
            #sys.exit()
        else:
            print(f'{package} cannot be found, would you like to install it (y/n)?')
            answer = input()
            if answer == 'y':
                #gitpython imports as git, annoying I know
                if package == 'git':
                    package = 'gitpython'
                os.system(f'pip install {package}')

#If user can load all libraries load GUI
from Launch_PyQt5 import main
main()
