import os
import shutil

import numpy as np

from numpy import dot
from numpy.linalg import norm

from Rearrange_Molecules import GEOM
from connectivity import find_connectivity

def determine_similarity(self):
    #Check if user has specified a valid directory
    directory = self.check_directory(self.ui.t1t4e_1.text())
    if directory == None: 
        self.ui.Console.setPlainText('Invalid directory selected')
        return

    mwl = [] #mass weighted coordinate list
    Files = sorted([x for x in os.listdir(directory) if x.endswith('.gjf')])
    Cinfo = f'Found {len(Files)} .gjf files in directory specified.\n'
    for File in Files:
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

    #Grab value specified by the user
    similarity_threshold = self.ui.t1t4dsb_1.value()

    failed = []
    for index1, mw1 in enumerate(mwl):
        if index1 in failed: continue
        for index2, mw2 in enumerate(mwl):
            if index2 <= index1 or index2 in failed: continue
            #similarity = round(dot(mw1, mw2)/(norm(mw1)*norm(mw2)),8)
            similarity = round(abs(1-np.average(np.array(mw1)/np.array(mw2))),8)
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