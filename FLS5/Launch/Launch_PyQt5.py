import os
import shutil
import sys

from subprocess import Popen

from FLS_5 import Ui_MainWindow
from GUI_Triggered import GUI_Calls
from Preferences import Root_Path, set_basis, Load_Preferences

import git

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

Path = os.path.dirname(os.path.realpath(__file__))
Icon_Path = os.path.join(os.path.split(Path)[0],'icons')

class AppWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
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
        self.ui.t2t4PB_1.clicked.connect(lambda: self.file_open('*.gjf'))
        self.ui.action_Check_for_updates.triggered.connect(lambda: self.Update(1))
        Root = os.getenv('APPDATA')
        if Root == None:
            font = QtGui.QFont()
            #font.setPointSize(8)
            font.setBold(False)
            #font.setWeight(50)
            self.ui.centralwidget.setFont(font)
        self.show()
        #print(os.path.realpath(__file__))
        self.Update(0)

    def file_open(self, file_type):
        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File','',file_type)
        if len(name) > 1: #Linux is funky
            name = name[0]
        self.ui.t2t4LE_1.setText(name)

    def mousePressEvent(self, event):
        focused_widget = QtWidgets.QApplication.focusWidget()
        if focused_widget == self.ui.t3PPTE_1:
            set_basis(self)
        try:
            focused_widget.clearFocus()
        except AttributeError:
            pass
        QtWidgets.QMainWindow.mousePressEvent(self, event)

    def check_directory(self, directory):
        directory = directory.strip()
        if os.path.isdir(directory) != True:
            directory = None
        return directory

    def close_application(self): #Exit alert for user
        choice_title = 'Exit Confirmation'
        choice_prompt = 'Are you sure you wish to close McMahon Suite?'
        choice = QtWidgets.QMessageBox.question(self, choice_title, choice_prompt, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()

    def closeEvent(self, event):
        event.ignore() #Do not let application close without prompt
        self.close_application() #Call the exit prompt

    def Update(self,Launch):
        repo_url = 'https://github.com/jrjfeath/Feather_Labs_Suite'
        
        #Delete temp directory or git download fails
        try: shutil.rmtree(f'{Root_Path(self)}/Temp')
        except FileNotFoundError: pass 
        #Try to download github repo
        try: repo = git.Repo.clone_from(repo_url, f'{Root_Path(self)}/Temp', branch='master')
        except: #Not sure of actual except handle
            self.ui.Console.setPlainText('Unable to access github, do you have an internet connection?')
            return
        repo_id = repo.head.object.hexsha

        with open(f'{Path}/ID.txt','r') as opf:
            local_id = opf.read().strip()

        if repo_id == local_id: #If the ids match then no changes
            if Launch != 0: self.ui.Console.setPlainText('No update is currently available.')
            return

        #Safely find top directory of github files
        subdir=os.path.split(Path)[0]
        topdir=os.path.split(subdir)[0]
        
        choice_title = 'Update Available'
        choice_prompt = 'An update is available, would you like to update?'
        choice = QtWidgets.QMessageBox.question(self, choice_title, choice_prompt, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            shutil.rmtree(topdir) #Delete old files
            shutil.move(f'{Root_Path(self)}/Temp',topdir) #Move new files
            with open(f'{Path}/ID.txt','w') as opf: #Update ID
                opf.write(repo_id)
            sys.exit() 

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = AppWindow()
    sys.exit(app.exec_())

sys._excepthook = sys.excepthook 
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback) 
    #sys.exit(1) 
sys.excepthook = exception_hook 