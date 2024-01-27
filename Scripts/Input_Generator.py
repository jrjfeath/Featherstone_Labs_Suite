import os
import re
import time
from Scripts.Atom_Info import *

def extract_input(self,tab):
    files = []
    if tab == 0: #Modify Input
        directory = self.check_directory(self.ui.t1de.text())
        if directory != None:
            files = [os.path.join(directory,f) for f in os.listdir(directory) if f.lower().endswith('.gjf')]
        chk = self.ui.Chk_drop.currentIndex()
        scr = self.ui.Scr_drop.currentIndex()
        rwf = self.ui.Rwf_drop.currentIndex()
        username = self.ui.gusr_entry.text()
        basis = self.ui.basis_entry.text()
        proc = self.ui.proc_entry.value()
        mem = self.ui.mem_entry.value()
        charge = self.ui.CHARGE_entry.value()
        multi = self.ui.Multi_entry.value()
        footer = self.ui.foote.toPlainText()
    else: #Convert log to gjf
        directory = self.check_directory(self.ui.t1de_2.text())  
        if directory != None:
            files = [os.path.join(directory,f) for f in os.listdir(directory) if f.lower().endswith('.log')]
        chk = self.ui.Chk_drop_2.currentIndex()
        scr = self.ui.Scr_drop_2.currentIndex()
        rwf = self.ui.Rwf_drop_2.currentIndex()
        username = self.ui.gusr_entry_2.text()
        basis = self.ui.basis_entry_2.text()
        proc = self.ui.proc_entry_2.value()
        mem = self.ui.mem_entry_2.value()
        charge = self.ui.CHARGE_entry_2.value()
        multi = self.ui.Multi_entry_2.value()
        footer = self.ui.foote_2.toPlainText()
    if len(files) > 0: #if files exist
        if not os.path.exists(os.path.join(directory,'New_Input')): #Check if directory exists
            os.makedirs(os.path.join(directory,'New_Input'))
        make_input(self,tab,directory,files,chk,scr,rwf,username,basis,proc,mem,charge,multi,footer)
    else:
        self.ui.Console.setPlainText('No files found in provided directory.')   
        
def make_input(self,tab,directory,files,chk,scr,rwf,username,basis,proc,memory,charge,multiplicity,footer):
    console_info = ''
    n = 0
    Ping = time.time()
    uni_c = 0 #Check input for unicode
    for file in files:
        if time.time()-Ping > 0.1:
            self.ui.progressBar.setValue(int((n/len(files))*100))
            Ping= time.time()
        file_name = os.path.basename(file)
        
        #####READ DATA FROM GJF#####
        if tab == 0:
            opf = open(file,'r')
            lines = opf.readlines()
            opf.close()
            geom_index = 0
            geometry=[] #Get geometry of atoms from file
            for line_index in range(len(lines)): #Find where the geometry begins
                split_line = lines[line_index].split() #Split line
                if len(split_line) == 4: #If line breaks into four sections
                    if '.' in split_line[1] and '.' in split_line[2] and '.' in split_line[3]: #if it fits geometry
                        if geometry == []:
                            geom_index = line_index #write the index
                        geometry.append(lines[line_index].split())
            if len(geometry) == 0: #If there is no xyz
                console_info += (file_name+' has no useable xyz coordinates.\n')
                self.ui.progressBar.setValue(int((n/len(files))*100))
                n+=1
                continue
        
        #####READ DATA FROM LOG#####
        else: 
            status = self.ui.t1t2CB_1.currentIndex()
            
            opf = open(file,'r') #open file
            data = opf.read() #read data
            opf.close() #close file

            completed=re.findall(r'Normal termination(.*?)of Gaussian',data) #See if job completed
            if len(completed) == 0 and status != 2: #If job failed and user did not select to use failed
                console_info += (file_name+' failed and user did not select to use failed files.\n')
                self.ui.progressBar.setValue(int((n/len(files))*100))
                n+=1
                continue
            
            IMG = re.findall(r'imaginary frequencies',data) #Check if log has imaginary frequencies
            if len(IMG) > 0 and status == 0:
                console_info += (file_name+' contains imaginary frequencies and user did not select to use these.\n')
                self.ui.progressBar.setValue(int((n/len(files))*100))
                n+=1
                continue           
            
            GEOM = re.findall(r'Standard orientation([\s\S]*?)Rotational constants',data)
            if len(GEOM) == 0: #Sometime frequency calculations are missing above block
                GEOM = re.findall(r'Axes restored to original set([\s\S]*?)Cartesian Forces',data)
            if len(GEOM) > 0:
                geometry = []
                for i in GEOM[-1].split('\n')[5:-2]:
                    i = i.split()
                    if len(i) == 6:
                        geometry.append([chemical_symbols[int(i[1])],i[3],i[4],i[5]])
                    else:
                        geometry.append([chemical_symbols[int(i[1])],i[2],i[3],i[4]])
            else:
                console_info += (file_name+' did not contain usable xyz coordinates, have you deleted something?\n')
                self.ui.progressBar.setValue(int((n/len(files))*100))
                n+=1
                continue

        ##### Write the data to a new file in a new directory #####
        file_name = file_name[:-4]
        fs = '' #empty string variable for writing to file
        if rwf == 0 and chk == 0 and scr == 0:
            fs+=f'%nosave\n'
        if rwf == 1:
            fs+=f'%rwf={file_name}.rwf\n'
        if rwf == 2:
            fs+=f'%rwf=/scratch/{username}/rwf/{file_name}.rwf\n'
        if rwf == 3:
            fs+=f'%rwf={file_name}.rwf\n%nosave\n'
        if scr == 1:
            fs+=f'%scr={file_name}.scr\n'
        if scr == 2:
            fs+=f'%scr=/scratch/{username}/scr/{file_name}.scr\n'
        if scr == 3:
            fs+=f'%scr={file_name}.scr\n%nosave\n'
        if chk == 1:
            fs+=f'%chk={file_name}.chk\n'
        if chk == 2:
            fs+=f'%chk=/scratch/{username}/chk/{file_name}.chk\n'          
        fs+=f'%mem={memory}mb\n'
        fs+=f'%nproc={proc}\n'
        fs+=f'{basis}\n\n'
        fs+=f'Original File: {file_name}\n\n'
        fs+=f'{charge} {multiplicity}\n'

        for i in geometry:
            fs+='%2s    %12s    %12s    %12s\n'%(i[0],i[1],i[2],i[3])
    
        if tab == 0: #If modifying inputs
            if self.ui.foot_drop.currentIndex() == 0:
                old_footer = lines[geom_index+len(geometry):]
                old_footer = [x.strip('\n') for x in old_footer if len(x.strip('\n').strip(' ')) > 0]
                if len(old_footer) > 0:
                    fs+='\n'
                    for i in old_footer:
                        fs+=f'{i}\n'
        fs+=f'\n{footer}'
        fs+='\n\n\n'

        for x in fs:
            if uni_c != 0: break #Skip if unicode has already been checked
            if ord(x) > 127:
                uni_c+=1
                uni_i = fs.find(x)
                console_info += (f'Unicode detected in input: {x}\n')
                console_info += (f'Unicode surrounded by {fs[uni_i-3:uni_i+3]}\n')
                console_info +=('Please remove or gaussian will crash.\n')
        if uni_c == 0:
            opf = open(os.path.join(directory,'New_Input',file_name+'.gjf'),'w')
            opf.write(fs)
            opf.close()    
        n+=1
    console_info += ('New files have been written to: '+os.path.join(directory,'New_Input')+'\n')
    self.ui.Console.setPlainText(console_info)  
    self.ui.progressBar.setValue(0)
