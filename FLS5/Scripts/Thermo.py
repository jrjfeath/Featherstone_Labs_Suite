import os
import re
import fnmatch
import time
import math
from SPE import check_file_closed

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
            type = 'Completed'
        else:
            type = 'All'
        if len(files) > 0:
            extract(self,type,files,directory)
        else:
            self.ui.Console.setPlainText('No output files in specified directory.')
    else:
        self.ui.Console.setPlainText('Invalid directory')
        
def extract(self,type,files,directory):
    CInfo = 'Starting extraction process for thermochemical data.\n'
    self.ui.Console.setPlainText(CInfo)
    String = ''
    Ping = time.time()
    for i in range(len(files)):
        if time.time()-Ping > 0.1:
            self.ui.progressBar.setValue((i)/len(files)*100)
            Ping = time.time()
        openfile = open(files[i],'r')
        text = openfile.read()
        openfile.close()
        Thermo_Pass = []
        if type == 'Completed': #If user does not want to use failed jobs
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
            ET = float(re.findall(r'Total                  (.*?) Electronic', text,re.DOTALL)[0].split()[2])
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
            
            #Write the data to the file
            format_line = '{:s},{:s},{:s},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f}\n'
            if self.ui.t2t2CB_2.currentIndex() == 0: FN = os.path.basename(files[i])
            else: FN = files[i]
            String += format_line.format(FN,IMG,MP,HF,ZPC,TCN,TCE,TCG,SEZ,SET,SETE,SETF,ET)
    if String == '': #If no data found
        CInfo += 'No thermochemical data found in files.'
        self.ui.Console.setPlainText(CInfo)
        self.ui.progressBar.setValue(0)
        return
    format_line = '{:s},{:s},{:s},{:s},{:s},{:s},{:s},{:s},{:s},{:s},{:s},{:s},{:s}\n'
    Header = format_line.format("Filename","Imaginary","Multiplicity","Energy","Zero-point correction","Thermal correction to Energy","Thermal correction to Enthalpy","Thermal correction to Gibbs Free Energy","Sum of electronic and zero-point Energies","Sum of electronic and thermal Energies","Sum of electronic and thermal Enthalpies","Sum of electronic and thermal Free Energies","Total S")
    csvname = check_file_closed(os.path.join(directory,'Thermo_Data'),'.csv')
    opf = open(csvname,'w')
    opf.write(Header+String)
    opf.close()
    CInfo += 'Process completed successfully.'
    self.ui.Console.setPlainText(CInfo)
    self.ui.progressBar.setValue(0)


