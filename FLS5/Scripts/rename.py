import os
import re 

def rename_files(self):
    directory = self.check_directory(self.ui.t1t3le_1.text())
    if directory:
        search = self.ui.t1t3le_2.text()
        replace = self.ui.t1t3le_3.text()
        ext_1 = self.ui.t1t3le_4.text().strip()
        ext_2 = self.ui.t1t3le_5.text().strip()
        #Check if user has input any values at all
        if search != '' or replace != '' or ext_1 != '' or ext_2 != '':
            rename(self,directory,search,replace,ext_1,ext_2)
        else:
            self.ui.Console.setPlainText('No parameters specified')
    else:
        self.ui.Console.setPlainText('Invalid directory')

def rename(self,directory,search,replace,ext_1,ext_2):
    #If no search value probably replacing extensions
    if search == '':
        Files = [x for x in os.listdir(directory) if x.endswith(ext_1)]
        #If user searches for nothing it makes a mess
        search = '$#12234567890#$'
    #If user is searching for a value without an extension
    elif search != '' and ext_1 == '':
        Files = [x for x in os.listdir(directory) if search in x]
    #User is most likely searching for word with certain extension
    else:
        Files = [x for x in os.listdir(directory) if search in x and x.endswith(ext_1)]
    #If no files found abort process
    if len(Files) == 0:
        self.ui.Console.setPlainText('No Files match search criteria')
        return
    #Make a copy of the files
    Originals = Files.copy()
    #Search for the provided string
    Files = [re.sub(search, replace, x) for x in Files]
    #If the user wants to rename extensions
    if ext_2 != '' and ext_1 != '':
        Files = [re.sub(ext_1, ext_2, x) for x in Files]
    info = ''
    for i in range(len(Originals)):
        try:
            os.rename(os.path.join(directory,Originals[i]),os.path.join(directory,Files[i]))
            info+='Successfully renamed: '+Originals[i]+' to '+Files[i]+'\n'
        except FileExistsError:
            info+='Cannot rename: '+Originals[i]+' to '+Files[i]+' another file already has that name!\n'
    self.ui.Console.setPlainText(info) 
