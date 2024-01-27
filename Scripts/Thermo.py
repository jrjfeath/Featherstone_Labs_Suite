import fnmatch
import math
import os
import re
import time
from Scripts.SPE import check_file_closed

def Extract_Thermo(self):
    directory = self.check_directory(self.ui.t2t2LE_1.text())
    if directory:
        if self.ui.t2t2CB_2.currentIndex() == 0:
            files = [os.path.join(directory,f) for f in os.listdir(directory) if f.lower().endswith('.log')]
        else: #If the user has selected to search recursively
            files = []
            #This process is windows and linux compatible
            for root, _, filenames in os.walk(directory):
                filenames = [x.lower() for x in filenames]
                for filename in fnmatch.filter(filenames, '*.log'):
                    files.append(os.path.join(root, filename))
        if self.ui.t2t2CB_1.currentIndex() == 0:
            Type = 'Completed'
        else:
            Type = 'All'
        if len(files) > 0:
            extract(self,Type,files,directory)
        else:
            self.ui.Console.setPlainText('No output files in specified directory.')
    else:
        self.ui.Console.setPlainText('Invalid directory')
        
def extract(self,Type,files,directory):
    CInfo = 'Starting extraction process for thermochemical data.\n'
    self.ui.Console.setPlainText(CInfo)
    
    Thermo_Data = {}
    Ping = time.time()
    for i in range(len(files)):
        if time.time()-Ping > 1.0: #only update once a second
            self.ui.progressBar.setValue(int((i)/len(files)*100))
            Ping = time.time()
        openfile = open(files[i],'r')
        text = openfile.read()
        openfile.close()
        Thermo_Pass = []
        if Type == 'Completed': #If user does not want to use failed jobs
            if 'Normal termination' in text:
                Thermo_Pass = re.findall(r'- Thermochemistry(.*?)\n',text) #Check if file has thermochemistry
        else:
            Thermo_Pass = re.findall(r'- Thermochemistry(.*?)\n',text) #Check if file has thermochemistry
            if Thermo_Pass == []:
                CInfo += 'All files selected but '+os.path.basename(files[i])+' does not contain thermochemical data.\n'
        if Thermo_Pass != []:
            ZPC = float(re.findall(r'Zero-point correction=(.*?)\(',text)[0].strip())
            TCN = float(re.findall(r'Thermal correction to Energy=(.*?)\n',text)[0].strip())
            TCE = float(re.findall(r'Thermal correction to Enthalpy=(.*?)\n',text)[0].strip())
            TCG = float(re.findall(r'Thermal correction to Gibbs Free Energy=(.*?)\n',text)[0].strip())
            SEZ = float(re.findall(r'Sum of electronic and zero-point Energies=(.*?)\n', text)[0].strip())
            SET = float(re.findall(r'Sum of electronic and thermal Energies=(.*?)\n', text)[0].strip())
            SETE = float(re.findall(r'Sum of electronic and thermal Enthalpies=(.*?)\n', text)[0].strip())
            SETF = float(re.findall(r'Sum of electronic and thermal Free Energies=(.*?)\n', text)[0].strip())
            ET = float(re.findall(r'Total   (.*?) Electronic', text,re.DOTALL)[0].split()[2])
            try: MP = re.findall(r'Multiplicity =(.*?)\n',text)[0].strip() 
            except IndexError: MP = 'N/A'
            
            if math.isnan(ZPC) == True: #Check if valid math in calculation
                CInfo += f"{os.path.basename(files[i])} has failed due to infinite energy.\n"
                continue #Too many negative frequencies in file sums to infinite corrections
            
            HF = SEZ-ZPC #Calculate the HF value
            
            #Check for negative frequencies
            IMG = re.findall(r'imaginary frequencies',text)
            if len(IMG) > 0: IMG = 'Yes' 
            else: IMG = 'No'

            #If searching recursively attach directory
            if self.ui.t2t2CB_2.currentIndex() == 0: FN = os.path.basename(files[i])
            else: FN = files[i]
            
            #Write data to dictionary
            Thermo_Data[FN] = [IMG,MP,HF,ZPC,TCN,TCE,TCG,SEZ,SET,SETE,SETF,ET]
    
    if len(Thermo_Data) == 0: #If no data found
        CInfo += 'No thermochemical data found in files.'
        self.ui.Console.setPlainText(CInfo)
        self.ui.progressBar.setValue(0)
        return

    #Sort our dictionary according to option select. k = key, v = key values
    DPI = self.ui.t2t2CB_3.currentIndex() #Get index of dropdown menu
    #Always sort by filename, overwrite order later
    Thermo_Data = {k: Thermo_Data[k] for k in sorted(Thermo_Data)}
    #If we dont sort by the filename we need to sort by a value in key
    if DPI == 1: #Electronic Energy (HF)
        index = 2 #Found above when declaring key values for dict
    if DPI == 2: #Enthalpy (SETE)
        index = 9
    if DPI == 3: #Free Energy (SETF)
        index = 10
    if DPI != 0: #If we aren't sorting by filename sort by the selected index
        Thermo_Data = {k: v for k, v in sorted(Thermo_Data.items(), key=lambda item: item[1][index])}

    #fetch minimum energy values in event user wants relative energies
    k1 = list(Thermo_Data.keys())[0] #Get the first key
    #Get the energies from the first key, electron, enthalpy, free energy
    min_e = [float(Thermo_Data[k1][2]),float(Thermo_Data[k1][9]),float(Thermo_Data[k1][10])]

    #Write the data to a string for file writing
    String = ''
    for key in Thermo_Data:
        String += f'{key},' #write key to string
        kd = Thermo_Data[key] #fetch key data (kd)
        for value in kd: String+=f'{value},' #write each value to string
        String = String[:-1] #Remove trailing comma
        
        #If the user selects relative values
        if DPI != 0 and self.ui.t2t2CB_4.currentIndex() == 1: 
            String += f',{(float(kd[2])-min_e[0])*2625.5},{(float(kd[9])-min_e[1])*2625.5},{(float(kd[10])-min_e[2])*2625.5}'
        
        String+='\n'

    #Header is quite long so it's seperated through multiple additions
    Header = "Filename,Imaginary,Multiplicity,Energy,"
    Header +="Zero-point correction,Thermal correction to Energy,"
    Header +="Thermal correction to Enthalpy,Thermal correction to Gibbs Free Energy,"
    Header +="Sum of electronic and zero-point Energies,Sum of electronic and thermal Energies,"
    Header +="Sum of electronic and thermal Enthalpies,Sum of electronic and thermal Free Energies,"
    Header +="Total S"
    #If user wants to include relative values
    if DPI != 0 and self.ui.t2t2CB_4.currentIndex() == 1:
        Header += ',Relative Electronic (kJ/mol),Relative Enthalpy (kJ/mol),Relative Free Energy (kJ/mol)'
    Header += '\n'
    csvname = check_file_closed(os.path.join(directory,'Thermo_Data'),'.csv')
    opf = open(csvname,'w')
    opf.write(Header+String)
    opf.close()
    CInfo += 'Process completed successfully.'
    self.ui.Console.setPlainText(CInfo)
    self.ui.progressBar.setValue(0)


