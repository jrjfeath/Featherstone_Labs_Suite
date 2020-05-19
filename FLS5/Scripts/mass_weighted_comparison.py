import os
import shutil

import numpy as np
from Rearrange_Molecules import GEOM

def determine_similarity(self):
    #Check if user has specified a valid directory
    directory = self.check_directory(self.ui.t1t4e_1.text())
    if directory == None: 
        self.ui.Console.setPlainText('Invalid directory selected')
        return

    mwl = [] #mass weighted coordinate list
    Files = sorted([x for x in os.listdir(directory) if x.endswith('.gjf')])
    for File in Files:
        with open(f'{directory}/{File}','r') as opf:
            lines = opf.readlines()
        geometry = ''
        for line in lines:
            line = line.split()
            if len(line) != 4: continue
            try: float(line[1]),float(line[2]),float(line[3])
            except ValueError: continue
            geometry += '   '.join(line)+'\n'
        md = GEOM(geometry) #molecule data
        distances = (md.comDist) #distances from center
        xyz = md.geom
        masses = xyz[:,0]
        mw = sorted(list(distances*masses))
        mwl.append(mw)

    #Grab value specified by the user
    #100-Value as I found it was more user friendly to ask that way
    similarity_threshold = (100-self.ui.t1t4dsb_1.value())/100

    failed = []
    for index1, mw1 in enumerate(mwl):
        if index1 in failed: continue
        for index2, mw2 in enumerate(mwl):
            if index2 <= index1 or index2 in failed: continue
            similarity = round(abs(1-np.average(np.array(mw1)/np.array(mw2))),4)
            if similarity < similarity_threshold:
                failed.append(index2)

    for index in sorted(failed,reverse=True):
        del Files[index]

    try: os.mkdir(f'{directory}/uniques')
    except FileExistsError: pass

    for File in Files:
        shutil.copy(f'{directory}/{File}',f'{directory}/uniques/{File}')