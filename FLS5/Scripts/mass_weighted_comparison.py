import os
import shutil

import numpy as np

from numpy import dot
from numpy.linalg import norm

from Rearrange_Molecules import GEOM
from connectivity import find_connectivity

def determine_similarity(self):
    #Check if user has specified a valid directory
    path = self.ui.t1t4e_1.text()
    directory = self.check_directory(path)
    #if directory is not valid user has specified csv or invalid directory
    if directory == None: 
        #Check that the path isnt empty
        if len(path) < 5: 
            self.ui.Console.setPlainText('Invalid directory selected')
            return
        if os.path.isfile(path) and path[-4:] == '.csv':
            with open(path,'r') as opf:
                lines = opf.readlines()
            Files = []
            for line in lines[1:]:
                line = line.split(',')
                Files.append(line[0][:line[0].rfind('.')]+'.gjf')
            directory = os.path.dirname(path)
        else:
            self.ui.Console.setPlainText('File specified needs to be a csv with filenames in the first column.')
            return
    #If it was a directory sort the files by filename
    else: Files = sorted([x for x in os.listdir(directory) if x.endswith('.gjf')])

    mwl = [] #mass weighted coordinate list
    Cinfo = f'Found {len(Files)} .gjf files in directory specified.\n'
    for File in Files:
        try:
            with open(f'{directory}/{File}','r') as opf:
                lines = opf.readlines()
                geometry = []
                labels = []
                for line in lines:
                    line = line.split()
                    if len(line) != 4: continue
                    try: 
                        geometry.append([float(line[1]),float(line[2]),float(line[3])])
                        labels.append(line[0])
                    except ValueError: continue
                geometry = np.array(geometry)
                mw = find_connectivity(labels,geometry)
                mwl.append(mw)
        except FileNotFoundError:
            try:
                with open(f'{directory}/Error.txt','a+') as erropf:
                    erropf.writelines(f'{File} \n')
            except FileNotFoundError:
                with open(f'{directory}/Error.txt','w') as erropf:
                    erropf.writelines("Unable to find the following file(s), please double check if they exist. \n")
                    erropf.writelines(f'{File} \n')


    #Grab value specified by the user
    similarity_threshold = self.ui.t1t4dsb_1.value()

    failed = []
    for index1, mw1 in enumerate(mwl):
        if index1 in failed: continue
        for index2, mw2 in enumerate(mwl):
            if index2 <= index1 or index2 in failed: continue
            #similarity = round(dot(mw1, mw2)/(norm(mw1)*norm(mw2)),8)
            try: similarity = round(abs(1-np.average(np.array(mw1)/np.array(mw2))),8)
            except ValueError: continue #If structures of two different sizes are compared
            if similarity < (100-similarity_threshold)/100:
                #print(Files[index1],Files[index2],mw1,mw2,similarity)
                failed.append(index2)

    for index in sorted(failed,reverse=True):
        del Files[index]

    try: os.mkdir(f'{directory}/uniques')
    except FileExistsError: pass

    for File in Files:
        shutil.copy(f'{directory}/{File}',f'{directory}/uniques/{File}')

    Cinfo+= f'After comparison found {len(Files)} unique geometries.'
    self.ui.Console.setPlainText(Cinfo)