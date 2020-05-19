import os
import re
import time
from Atom_Info import *

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
    for file in files:
        if time.time()-Ping > 0.1:
            self.ui.progressBar.setValue((n/len(files))*100)
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
                self.ui.progressBar.setValue((n/len(files))*100)
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
                self.ui.progressBar.setValue((n/len(files))*100)
                n+=1
                continue
            
            IMG = re.findall(r'imaginary frequencies',data) #Check if log has imaginary frequencies
            if len(IMG) > 0 and status == 0:
                console_info += (file_name+' contains imaginary frequencies and user did not select to use these.\n')
                self.ui.progressBar.setValue((n/len(files))*100)
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
                self.ui.progressBar.setValue((n/len(files))*100)
                n+=1
                continue

        ##### Write the data to a new file in a new directory #####
        file_name = file_name[:-4]
        opf = open(os.path.join(directory,'New_Input',file_name+'.gjf'),'w')
        if rwf == 0 and chk == 0 and scr == 0:
            opf.write('%nosave\n')
        if rwf == 1:
            opf.write('%rwf='+file_name+'.rwf\n')
        if rwf == 2:
            opf.write('%rwf=/scratch/'+username+'/rwf/'+file_name+'.rwf\n')
        if rwf == 3:
            opf.write('%rwf='+file_name+'.rwf\n%nosave\n')
        if scr == 1:
            opf.write('%scr='+file_name+'.scr\n')
        if scr == 2:
            opf.write('%scr=/scratch/'+username+'/scr/'+file_name+'.scr\n')
        if scr == 3:
            opf.write('%scr='+file_name+'.scr\n%nosave\n')
        if chk == 1:
            opf.write('%chk='+file_name+'.chk\n')
        if chk == 2:
            opf.write('%chk=/scratch/'+username+'/chk/'+file_name+'.chk\n')            
        opf.write('%mem='+str(memory)+'mb\n')
        opf.write('%nproc='+str(proc)+'\n')
        opf.write(basis+'\n\n')
        opf.write('Original File: '+file_name+'\n\n')
        opf.write(str(charge)+' '+str(multiplicity)+'\n')

        for i in geometry:
            opf.write('%2s    %12s    %12s    %12s\n'%(i[0],i[1],i[2],i[3]))
    
        if tab == 0: #If modifying inputs
            if self.ui.foot_drop.currentIndex() == 0:
                old_footer = lines[geom_index+len(geometry):]
                old_footer = [x.strip('\n') for x in old_footer if len(x.strip('\n').strip(' ')) > 0]
                if len(old_footer) > 0:
                    opf.write('\n')
                    for i in old_footer:
                        opf.write(i+'\n')
        opf.write('\n'+footer)
        opf.write('\n\n\n')
        opf.close()    
        n+=1
    console_info += ('New files have been written to: '+os.path.join(directory,'New_Input')+'\n')
    self.ui.Console.setPlainText(console_info)  
    self.ui.progressBar.setValue(0)
