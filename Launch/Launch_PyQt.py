import errno
import os
import platform
import shutil
import stat
import subprocess
import sys

from pathlib import Path

from .GUI_Triggered import GUI_Calls
from .Preferences import set_basis, Load_Preferences

import git
import requests

from PyQt6 import uic, QtWidgets, QtCore, QtGui

path = Path(os.path.dirname(os.path.realpath(__file__)))
Icon_Path = os.path.join(os.path.split(path)[0],'icons')

#filename for the ui file
uifn = f"{path}/FLS.ui"

class AppWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(uifn,self)
        Load_Preferences(self)
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('cleanlooks'))
        app_icon = QtGui.QIcon()
        app_icon.addFile(os.path.join(Icon_Path,'Cup_16.png'), QtCore.QSize(16,16))
        app_icon.addFile(os.path.join(Icon_Path,'Cup_24.png'), QtCore.QSize(24,24))
        app_icon.addFile(os.path.join(Icon_Path,'Cup_32.png'), QtCore.QSize(32,32))
        app_icon.addFile(os.path.join(Icon_Path,'Cup_48.png'), QtCore.QSize(48,48))
        app_icon.addFile(os.path.join(Icon_Path,'Cup_256.png'), QtCore.QSize(256,256))
        self.setWindowIcon(app_icon)
        GUI_Calls(self) 
        self.ui.t2t4PB_1.clicked.connect(lambda: self.file_open('*.gjf','t2t4PB_1'))
        self.ui.t1t4pb.clicked.connect(lambda: self.file_open('*.csv','t1t4pb'))
        self.ui.action_Check_for_updates.triggered.connect(lambda: self.Update(1))
        self.ui.t2t2CB_3.currentIndexChanged.connect(lambda: self.enable_relative())
        git_path = os.getenv('APPDATA')
        if git_path == None:
            font = QtGui.QFont()
            #font.setPointSize(8)
            font.setBold(False)
            #font.setWeight(50)
            self.ui.centralwidget.setFont(font)
        self.show()
        self.Update(0)

    def file_open(self, file_type, which_button):
        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File','',file_type)
        if len(name) > 1: #Linux stores name in tuple
            name = name[0]
        if which_button == 't2t4PB_1': self.ui.t2t4LE_1.setText(name)
        else: self.ui.t1t4e_1.setText(name)

    def mousePressEvent(self, event):
        #If user enters new basis update dropdown
        focused_widget = QtWidgets.QApplication.focusWidget()
        if focused_widget == self.ui.t3PPTE_1:
            set_basis(self)
        try:
            focused_widget.clearFocus()
        except AttributeError:
            pass
        QtWidgets.QMainWindow.mousePressEvent(self, event)

    def enable_relative(self):
        '''Only allow relative energies if sorting by energy.'''
        if self.ui.t2t2CB_3.currentIndex() != 0: self.ui.t2t2CB_4.setEnabled(True)
        else:self.ui.t2t2CB_4.setEnabled(False)

    def check_directory(self, directory):
        directory = directory.strip()
        if os.path.isdir(directory) != True:
            directory = None
        return directory

    def close_application(self): #Exit alert for user
        choice_title = 'Exit Confirmation'
        choice_prompt = 'Are you sure you wish to close McMahon Suite?'
        choice = QtWidgets.QMessageBox.question(self, choice_title, choice_prompt, QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if choice == QtWidgets.QMessageBox.StandardButton.Yes:
            sys.exit()

    def closeEvent(self, event):
        event.ignore() #Do not let application close without prompt
        self.close_application() #Call the exit prompt

    def Update(self,Launch):
        
        def get_latest_commit():
            '''Check the sha of the latest commit without cloning.'''
            url = f"https://api.github.com/repos/jrjfeath/Featherstone_Labs_Suite/commits"
            response = requests.get(url)
            if response.status_code == 200:
                commits = response.json()
                latest_commit = commits[0]
                commit_sha = latest_commit['sha']
                commit_message = latest_commit['commit']['message']
                commit_url = latest_commit['html_url']
                return {
                    'sha': commit_sha,
                    'message': commit_message,
                    'url': commit_url,
                    'error': None
                }
            else:
                return {
                    'sha': None,
                    'message': None,
                    'url': None,
                    'error': response.status_code
                }
        # Get parent directory of script 
        parent_path = os.path.split(path)[0]
        # Create a path to download the git files to
        root = os.path.expanduser('~')
        git_path  = os.path.join(root,'FLS5')

        repo = get_latest_commit()
        if repo['error'] != None:
            self.ui.Console.setPlainText(f"Unable to access github, requests error: {repo['error']}")
            return

        id_file = Path(f'{parent_path}/ID.txt')
        # Check if an ID file exists, if it doesnt make one
        if not os.path.isfile(id_file):
            with open(id_file,'w') as opf:
                opf.write(repo['sha'])

        with open(id_file,'r') as opf:
            local_id = opf.read().strip()

        if repo['sha'] == local_id: #If the ids match then no changes
            if Launch != 0: self.ui.Console.setPlainText('No update is currently available.')
            return
        
        choice_title = 'Update Available'
        choice_prompt = 'An update is available, would you like to update?'
        choice = QtWidgets.QMessageBox.question(self, choice_title, choice_prompt, QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if choice == QtWidgets.QMessageBox.StandardButton.Yes:
            # Remove any pre-existing git files if they exist
            try: shutil.rmtree(git_path, ignore_errors=False)
            except FileNotFoundError: pass 
            #Try to download github repo
            repo_url = 'https://github.com/jrjfeath/Featherstone_Labs_Suite'
            try: git.Repo.clone_from(repo_url, git_path, branch='master')
            except: #Not sure of actual except handle
                self.ui.Console.setPlainText('Unable to access github, do you have an internet connection?')
                return
            with open(id_file,'w') as opf: #Update ID
                opf.write(repo['sha'])

            #Updating on windows
            if platform.system() == 'Windows':
                with open(Path(f'{git_path}/update.py'),'w') as opf:
                    opf.write('import shutil\n')
                    opf.write('import subprocess\n')
                    opf.write('from distutils.dir_util import copy_tree\n')
                    opf.write(f'copy_tree(r"{git_path}",r"{parent_path}")\n') #Move new files
                    opf.write(f'shutil.rmtree(r"{git_path},ignore_errors=True)\n') #Delete old files
                    opf.write(f'subprocess.Popen(r"{git_path}/Launcher.py",shell=True)')
                subprocess.Popen(f'{git_path}/update.py',shell=True)
                sys.exit() 
            #Updating on Linux
            else:
                shutil.move(git_path,parent_path) #Move new files
                shutil.rmtree(git_path,ignore_errors=True) #Delete old files
                sys.exit()

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = AppWindow()
    sys.exit(app.exec())

sys._excepthook = sys.excepthook 
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback) 
    #sys.exit(1) 
sys.excepthook = exception_hook 