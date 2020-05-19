#GUI required libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Change_Log(QMainWindow): #Create GUI Class

    ##########################################################
    #####~~~~~~~~~~/~~~~~~ GUI ELEMENTS ~~~~~~/~~~~~~~~~~#####
    ##########################################################
    
    def __init__(self): #Create Frame
        super(Change_Log, self).__init__()
        self.setGeometry(50,150,400,250)
        self.setFixedSize(self.size())
        self.setWindowTitle('McMahon Suite Change Log')
        app_icon = QIcon()
        app_icon.addFile('Cup_16.png', QSize(16,16))
        app_icon.addFile('Cup_24.png', QSize(24,24))
        app_icon.addFile('Cup_32.png', QSize(32,32))
        app_icon.addFile('Cup_48.png', QSize(48,48))
        app_icon.addFile('Cup_256.png', QSize(256,256))
        self.setWindowIcon(app_icon)
        QApplication.setStyle(QStyleFactory.create('cleanlooks'))


        info = ["""
Version 4.0.8
- Added Recursive searching to SPE and Thermo Extraction tools
- Fixed a compatability error with g16 log files for extraction

Version 4.0.7
- Added change log.
- Temporarily removed help and preference buttons as they do nothing.

Version 4.0.6
- Fixed the ability to specify a username in Convert Output to Input tab.

Version 4.0.5
Computed Spectrum Changes:
- Added Anharmonic Computed spectrum extraction.
- Added ability to specify relative intensities.

Version 4.0.4
- Fixed header error in Modify Input and Convert Output to Input tabs.

Version 4.0.3
- Added Footer Info to Modify Input and Convert Output to Input tabs.

Version 4.0.2
- Added Extraction Tools.

Version 4.0.1
- Added G16 to G09 Converter and Rename Files tabs.

Version 4.0.0
- Recoded GUI into pyqt for better stability and ease of use for user.
- Added Modify Input and Convert Output to Input tabs.
               """]

        lbl = QTextEdit('',self)
        lbl.setText(info[0])
        lbl.setReadOnly(True)
        lbl.setGeometry(0,0,400,250)
