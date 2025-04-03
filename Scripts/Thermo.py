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
            files = [os.path.join(directory,f) for f in os.listdir(directory) if f[-4:].lower() in ['.log','.out']]
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

def orca_thermo(data,filename, CInfo):

    def find_energy(string):
        nonlocal CInfo
        value = 0
        if string == "Multiplicity           Mult": end_string = '\n'
        else: end_string = " Eh"
        string_found = re.findall(f'{string}(.*?){end_string}', data)[0].replace('....','').replace('...','')
        try: value = float(string_found.strip())
        except IndexError: CInfo += f'Unable to find {string} in {filename}'
        return value

    #Format it the same as you would guassian
    ar = {
        "Electronic Energy" : 0,
        "Enthalpy" : 0,
        "Free Energy" : 0,
        "Entropy" : 0,
        "Zero-point Energy" : 0,
        "Zero-point Correction" : 0,
        "Thermal Correction to Energy" : 0,
        "Thermal Correction to Enthalpy" : 0,
        "Thermal Correction to Free Energy" : 0,
        "Multiplicity" : 'N/A',
        "Imaginary Frequencies" : False
    }

    try:
        ar["Electronic Energy"] = find_energy("Electronic energy")
        ar["Enthalpy"] = find_energy("Total Enthalpy")
        ar["Free Energy"] = find_energy("Final Gibbs free energy")
        ar["Entropy"]= find_energy("Final entropy term")*4.184 # fine to keep this in J/molK
        ar["Zero-point Correction"] = find_energy("Zero point energy")
        ar["Zero-point Energy"] = ar["Electronic Energy"] + ar["Zero-point Correction"]
        ar['Thermal Correction to Energy'] = find_energy("Total correction")
        ar["Thermal Correction to Enthalpy"] = ar['Thermal Correction to Energy'] + find_energy("Thermal Enthalpy correction")
        ar["Thermal Correction to Free Energy"] = ar["Free Energy"] - ar["Electronic Energy"]
        ar["Multiplicity"] = find_energy("Multiplicity           Mult")
    except IndexError: 
        CInfo += f'Error in {filename}.'
    return ar, CInfo

def gaussian_thermo(Type,text,filename,CInfo):

    def find_energy(string):
        nonlocal CInfo
        value = 0
        if string == "Zero-point correction=": end_string = r'\('
        else: end_string = "\n"
        try: value = float(re.findall(f'{string}(.*?){end_string}',text)[0].strip())
        except IndexError: CInfo += f'Unable to find {string} in {filename}'
        return value 

    Thermo_Pass = []
    if Type == 'Completed': #If user does not want to use failed jobs
        if 'Normal termination' in text:
            Thermo_Pass = re.findall(r'- Thermochemistry(.*?)\n',text) #Check if file has thermochemistry
    else:
        Thermo_Pass = re.findall(r'- Thermochemistry(.*?)\n',text) #Check if file has thermochemistry
        if Thermo_Pass == []:
            CInfo += 'All files selected but '+os.path.basename(filename)+' does not contain thermochemical data.\n'

    ar = {
        "Electronic Energy" : 0,
        "Enthalpy" : 0,
        "Free Energy" : 0,
        "Entropy" : 0,
        "Zero-point Energy" : 0,
        "Zero-point Correction" : 0,
        "Thermal Correction to Energy" : 0,
        "Thermal Correction to Enthalpy" : 0,
        "Thermal Correction to Free Energy" : 0,
        "Multiplicity" : 'N/A',
        "Imaginary Frequencies" : False
    }

    if Thermo_Pass != []:
        ar['Zero-point Correction'] = find_energy("Zero-point correction=")
        ar['Thermal Correction to Energy'] = find_energy("Thermal correction to Energy=")
        ar['Thermal Correction to Enthalpy'] = find_energy("Thermal correction to Enthalpy=")
        ar['Thermal Correction to Free Energy'] = find_energy("Thermal correction to Gibbs Free Energy=")
        ar['Zero-point Energy'] = find_energy("Sum of electronic and zero-point Energies=")
        ar['Electronic Energy'] = ar['Zero-point Energy']-ar['Zero-point Correction']
        ar['Enthalpy'] = find_energy( "Sum of electronic and thermal Enthalpies=")
        ar['Free Energy'] = find_energy("Sum of electronic and thermal Free Energies=")
        ar['Entropy'] = float(re.findall(r'Total   (.*?) Electronic', text,re.DOTALL)[0].split()[2]) * 4.184
        try: ar['Multiplicity'] = re.findall(r'Multiplicity =(.*?)\n',text)[0].strip() 
        except IndexError: pass
        
        if math.isnan(ar['Zero-point Correction']) == True: #Check if valid math in calculation
            CInfo += f"{os.path.basename(filename)} has failed due to infinite energy.\n"
        
        #Check for negative frequencies
        if len(re.findall(r'imaginary frequencies',text)) > 0: ar['Imaginary Frequencies'] = True

    return ar, CInfo

def extract(self,Type,files,directory):
    CInfo = 'Starting extraction process for thermochemical data.\n'
    self.ui.Console.setPlainText(CInfo)
    
    Thermo_Data = {}
    Ping = time.time()
    for i in range(len(files)):
        filename = files[i]
        if time.time()-Ping > 1.0: #only update once a second
            self.ui.progressBar.setValue(int((i)/len(files)*100))
            Ping = time.time()

        #Read from file
        with open(filename,'r') as opf:
            data = opf.read()

        #If searching recursively attach directory
        if self.ui.t2t2CB_2.currentIndex() == 0: FN = os.path.basename(filename)
        else: FN = filename

        if filename[-4:].lower() == '.log': Thermo_Data[FN], CInfo = gaussian_thermo(Type,data,filename,CInfo)
        if filename[-4:].lower() == '.out': Thermo_Data[FN], CInfo = orca_thermo(data,filename,CInfo)
    
    if len(Thermo_Data) == 0: #If no data found
        CInfo += 'No thermochemical data found in files.'
        self.ui.Console.setPlainText(CInfo)
        self.ui.progressBar.setValue(0)
        return

    #Sort our dictionary according to option select. k = key, v = key values
    DPI = self.ui.t2t2CB_3.currentIndex() #Get index of dropdown menu
    #Always sort by filename, overwrite order later
    Thermo_Data = dict(sorted(Thermo_Data.items()))
    #If we dont sort by the filename we need to sort by a value in key
    if DPI == 1: #Electronic Energy 
        index = "Thermal Energy"
    if DPI == 2: #Enthalpy 
        index = "Enthalpy"
    if DPI == 3: #Free Energy 
        index = "Free Energy"
    if DPI != 0: #If we aren't sorting by filename sort by the selected index
        Thermo_Data = dict(sorted(Thermo_Data.items(), key=lambda item: item[1][index]))

    #Get the minimum dictionary entry for comparing energies
    minimum_key = next(iter(Thermo_Data))
    minimum = Thermo_Data[minimum_key]
    String = ''
    for key, values in Thermo_Data.items():
        String += f'{key},' #write key to string
        for value in values: String+=f'{Thermo_Data[key][value]},' #write each value to string
        String = String[:-1] #Remove trailing comma
        
        #If the user selects relative values - these ones in kJ/mol :)
        if DPI != 0 and self.ui.t2t2CB_4.currentIndex() == 1: 
            String += f',{Thermo_Data[key]["Thermal Energy"] - minimum["Thermal Energy"] * 2625.5}'
            String += f',{Thermo_Data[key]["Enthalpy"] - minimum["Enthalpy"] * 2625.5 }'
            String += f',{Thermo_Data[key]["Free Energy"] - minimum["Free Energy"] * 2625.5}'
        
        String+='\n'

    #Header is quite long so it's seperated through multiple additions
    Header = f"Filename,"
    for key in minimum.keys():
        Header += f"{key},"
    Header = Header[:-1] #Remove trailing comma
    #If user wants to include relative values
    if DPI != 0 and self.ui.t2t2CB_4.currentIndex() == 1:
        Header += ',Relative Electronic,Relative Enthalpy,Relative Free Energy'
    Header += '\n'
    csvname = check_file_closed(os.path.join(directory,'Thermo_Data'),'.csv')
    opf = open(csvname,'w')
    opf.write(Header+String)
    opf.close()
    CInfo += 'Process completed successfully.'
    self.ui.Console.setPlainText(CInfo)
    self.ui.progressBar.setValue(0)


