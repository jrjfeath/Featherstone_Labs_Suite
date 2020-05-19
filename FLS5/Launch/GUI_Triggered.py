#Tab 1
from Input_Generator import extract_input
from rename import rename_files
from mass_weighted_comparison import determine_similarity

#Tab 2
from SPE import Extract_SPE
from Thermo import Extract_Thermo
from Spectrum import spectrum
from rotate_gjf import rotate_gjf
from Mass_Properties import Mass_Props

#Tab 3
from Preferences import preferences

def submit_button(self):
    pt_index = self.ui.tabWidget.currentIndex()
    if pt_index == 0:
        ct_index = self.ui.tabWidget_2.currentIndex()
        if ct_index == 0:
            extract_input(self,0)
        if ct_index == 1:
            extract_input(self,1)
        if ct_index == 2:
            rename_files(self)
        if ct_index == 3:
            determine_similarity(self)
    if pt_index == 1:
        ct_index = self.ui.tabWidget_3.currentIndex()
        if ct_index == 0:
            Extract_SPE(self)
        if ct_index == 1:
            Extract_Thermo(self)
        if ct_index == 2:
            spectrum(self)
        if ct_index == 3:
            rotate_gjf(self)
        if ct_index == 4:
            Mass_Props(self)
    if pt_index == 2:
        preferences(self)

def GUI_Calls(self):
    self.ui.action_Exit.triggered.connect(self.close_application)
    self.ui.pushButton.clicked.connect(lambda: submit_button(self))