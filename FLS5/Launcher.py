'''Checks if the user has the required python packages and launches if true.'''

import importlib
import os
import sys

CWD = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(CWD, 'Scripts'))
sys.path.append(os.path.join(CWD, 'Icons'))
sys.path.append(os.path.join(CWD, 'Launch'))

#Required Packages to run the script, ask user to install if not present
rp = ['PyQt5','numpy','xlsxwriter','git']
for package in rp:
    try: globals()[package] = importlib.import_module(package)
    except ModuleNotFoundError:
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
