import fnmatch
import os
import re
import sys
import time

from shutil import move

def Extract_SPE(self):
    directory = self.check_directory(self.ui.t2t1LE_1.text())
    if directory:
        #Check if user wants to search recursively
        if self.ui.t2t1CB_2.currentIndex() == 0:
            files = [os.path.join(directory,f) for f in os.listdir(directory) if f.lower().endswith('.log')]
        else: #If the user has selected to search recursively
            files = []
            #This process is windows and linux compatible
            for root, _, filenames in os.walk(directory):
                filenames = [x.lower() for x in filenames]
                for filename in fnmatch.filter(filenames, '*.log'):
                    files.append(os.path.join(root, filename))
        #Single Point Type
        if self.ui.t2t1CB_1.currentIndex() == 0: Type = 'HF'
        elif self.ui.t2t1CB_1.currentIndex() == 1: Type = 'MP2'
        else: Type = 'CCSD'
        #Determine if there are files to analyze
        if len(files) > 0: extract(self,Type,files,directory)
        else: self.ui.Console.setPlainText('No output files in specified directory.')
    else:
        self.ui.Console.setPlainText('Invalid directory')

#Function to read SPE data from file
def open_file(filename,byte_size):
    fp = open(filename, 'r+b')
    fp.seek(-byte_size, 2)
    data = str(fp.read(byte_size))
    fp.close()
    data = (''.join(data.split()))
    data = data.replace('\\n','')
    data = data.replace('\\r','')
    return data

#Function to grab specific energies
def extract_energy(Type,data):
    Value = ''
    if Type == 'HF': #look for HF
        Value = re.findall(r'H\s*F\s*=\s*(.*?)[\|\\]',data)
    if Type == 'MP2': #look for mp2
        Value = re.findall(r'M\s*P\s*2\s*=\s*(.*?)[\|\\]',data)
    if Type == 'CCSD': #look for CCSD
        Value = re.findall(r'C\s*C\s*S\s*D\s*=\s*(.*?)[\|\\]',data)
    if Value:
        Value = Value[-1].replace('\n','').replace(' ','')
        return float(Value)
    else:
        return None

#Check if the user has closed the file
def check_file_closed(filename,ext):
    Closed = False
    num = -1
    while Closed == False:
        num+=1
        csvname = filename+'_'+str(num)+ext
        try:
            opf = open(csvname,'w')
            opf.close()
            Closed = True
        except PermissionError:
            pass
    return csvname

def extract(self,Type,files,directory):
    CInfo = 'Starting extraction process for '+Type+' energies.\n'
    self.ui.Console.setPlainText(CInfo)
    search_byte=10000 #default search byte value
    SPE_F = {} #Empty dictionary for failed jobs
    SPE_G = [] #Empty list for energies
    Duplicates = False
    Ping = time.time()
    for i in range(len(files)):
        if time.time()-Ping > 0.1:
            self.ui.progressBar.setValue(int((i)/len(files)*100))
            Ping = time.time()
        byte_size = os.stat(files[i])[6] #Get the size of the file
        if byte_size < search_byte: #If file smaller than 10kb
            data = open_file(files[i],byte_size)
        if byte_size > search_byte: #If file larger than 10kb
            data = open_file(files[i],search_byte)
        if 'Normaltermination' in data: #If job successfully finished                  
            Value = extract_energy(Type,data)
            if not Value: #If normal termination and no value search whole file
                data = open_file(files[i],byte_size)
                Value = extract_energy(Type,data)
            if Value: #If a value is found for SPE
                Duplicate = [True for x in SPE_G if Value in x]
                if True in Duplicate:
                    Duplicates = True
                    #If you want to remove duplicates
                    if self.ui.t2t1CB_4.currentIndex() == 1 or self.ui.t2t1CB_3.currentIndex() == 1: 
                        continue
                SPE_G.append([Value,files[i]])
            else: #If value cannot be found, i.e extracting MP2 in HF files
                CInfo += ('Problem extracting energy from : '+os.path.basename(files[i])+'\n')
                SPE_F[files[i]]='Cannot find energy? Wrong job Type?'
        elif 'Error termination via Lnk1e' in data: #If job errors out
            CInfo += ('There is an error in the following job : '+os.path.basename(files[i])+'\n')
            Error = re.findall(r'Error termination via Lnk1e in(.*?)at',data)[0].replace('/','\\')
            SPE_F[files[i]]=Error
        else: #If no end card (thanks Graham)
            CInfo += ('The following job has not finished : '+os.path.basename(files[i])+'\n')
            SPE_F[files[i]]='Incomplete Job'
    if len(SPE_G) > 0: #If Energy values exist
        Ordered = sorted(SPE_G)
        #If duplicate files found and move uniques true and recursive false
        if Duplicates == True and self.ui.t2t1CB_3.currentIndex() == 1 and self.ui.t2t1CB_2.currentIndex() == 0: 
            if os.path.isdir(os.path.join(directory,'Uniques')) == False:
                os.mkdir(os.path.join(directory,'Uniques'))
            directory = os.path.join(directory,'Uniques')
        min_e = Ordered[0][0] #fetch minimum energy
        Filename = Type+'_Energies'
        csvname = check_file_closed(os.path.join(directory,Filename),'.csv')
        opf = open(csvname,'w')
        opf.write('Filename,Electronic Energy,Relative Energy (kJ/mol)\n')
        for i in Ordered: 
            #If user is not searching recursively
            if self.ui.t2t1CB_2.currentIndex() == 0:
                opf.write(f'{os.path.basename(i[1])},{i[0]},{(i[0]-min_e)*2625.5}\n')
            else:
                opf.write(f'{i[1]},{i[0]},{(i[0]-min_e)*2625.5}\n')
            #If the user selected to move files, only move files if it is not recursive
            if self.ui.t2t1CB_3.currentIndex() == 1 and self.ui.t2t1CB_2.currentIndex() == 0: 
                nl = os.path.join(directory,os.path.basename(i[1]))
                move(i[1],nl)
        opf.close()
        CInfo += 'Wrote SPE data to '+csvname+'\n'
    if len(SPE_F) > 0: #If errors exist
        csvname = check_file_closed(os.path.join(directory,Type+'_Failed'),'.csv')
        opf = open(csvname,'w')
        for i in SPE_F:
            opf.write(i+','+SPE_F[i]+'\n')
        opf.close()
        CInfo += 'Wrote failed files to '+csvname+'\n'
    CInfo += 'Finished processing files.'
    self.ui.Console.setPlainText(CInfo)
    self.ui.progressBar.setValue(0)
