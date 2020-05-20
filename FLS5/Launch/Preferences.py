import os

from pathlib import Path

def Root_Path():
    Root = os.getenv('APPDATA')
    if Root == None:
        Root = os.getenv('HOME')
    path = os.path.join(Root,'FLS5')
    if os.path.isdir(path) == False:
        os.mkdir(path)
    return Path(path)

def preferences(self):
    path = Root_Path()
    String = str(self.ui.t3PQB_1.currentIndex())+'\n'
    String += str(self.ui.t3PQB_2.currentIndex())+'\n'
    String += str(self.ui.t3PQB_3.currentIndex())+'\n'
    String += str(self.ui.t3PLE_1.text())+'\n'
    String += str(self.ui.t3PQB_4.currentText())+'\n'
    String += str(self.ui.t3PSB_1.value())+'\n'
    String += str(self.ui.t3PSB_2.value())+'\n'
    String += str(self.ui.t3PSB_3.value())+'\n'
    String += str(self.ui.t3PSB_4.value())+'\n'
    String += str(self.ui.t3PPTE_1.toPlainText())
    opf = open(os.path.join(path,'Preference.txt'),'w')
    opf.write(String)
    opf.close()
    Load_Preferences(self)

def Load_Preferences(self):
    path = Root_Path()
    #If the user has never launched the program before
    if os.path.isfile(os.path.join(path,'Preference.txt')) == False:
        preferences(self)
    opf = open(os.path.join(path,'Preference.txt'),'r')
    Lines = opf.readlines()
    opf.close()
    #Set Modify Input Files parameters
    self.ui.Rwf_drop.setCurrentIndex(int(Lines[0].strip()))
    self.ui.Scr_drop.setCurrentIndex(int(Lines[1].strip()))
    self.ui.Chk_drop.setCurrentIndex(int(Lines[2].strip()))
    self.ui.gusr_entry.setText(Lines[3].strip())
    self.ui.basis_entry.setText(Lines[4].strip())
    self.ui.proc_entry.setValue(int(Lines[5].strip()))
    self.ui.mem_entry.setValue(int(Lines[6].strip()))
    self.ui.CHARGE_entry.setValue(int(Lines[7].strip()))
    self.ui.Multi_entry.setValue(int(Lines[8].strip()))
    #Set Convert Out to In parameters
    self.ui.Rwf_drop_2.setCurrentIndex(int(Lines[0].strip()))
    self.ui.Scr_drop_2.setCurrentIndex(int(Lines[1].strip()))
    self.ui.Chk_drop_2.setCurrentIndex(int(Lines[2].strip()))
    self.ui.gusr_entry_2.setText(Lines[3].strip())
    self.ui.basis_entry_2.setText(Lines[4].strip())
    self.ui.proc_entry_2.setValue(int(Lines[5].strip()))
    self.ui.mem_entry_2.setValue(int(Lines[6].strip()))
    self.ui.CHARGE_entry_2.setValue(int(Lines[7].strip()))
    self.ui.Multi_entry_2.setValue(int(Lines[8].strip()))
    #Set Preferences
    self.ui.t3PQB_3.setCurrentIndex(int(Lines[0].strip()))
    self.ui.t3PQB_2.setCurrentIndex(int(Lines[1].strip()))
    self.ui.t3PQB_1.setCurrentIndex(int(Lines[2].strip()))
    self.ui.t3PLE_1.setText(Lines[3].strip())
    self.ui.t3PSB_1.setValue(int(Lines[5].strip()))
    self.ui.t3PSB_2.setValue(int(Lines[6].strip()))
    self.ui.t3PSB_3.setValue(int(Lines[7].strip()))
    self.ui.t3PSB_4.setValue(int(Lines[8].strip()))
    set_basis(self,Lines)

def set_basis(self,Lines):
    self.ui.t3PPTE_1.setPlainText(''.join(Lines[9:]))
    self.ui.t3PQB_4.clear()
    Options = self.ui.t3PPTE_1.toPlainText().split('\n')
    for i in range(len(Options)):
        self.ui.t3PQB_4.addItem(Options[i])
        if Options[i] == Lines[4].strip():
            self.ui.t3PQB_4.setCurrentIndex(i)