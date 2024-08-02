import os
import time
import numpy as np

from thermoanalysis.QCData import QCData
from thermoanalysis.thermo import thermochemistry

fields = ["T","U_tot","H","G"]

def get_thermos(thermos):
    filtered = []
    for thermo in thermos:
        values = [getattr(thermo, f) for f in fields]
        filtered.append(values)
    return np.array(filtered)

def analyze_temperature(self):
    #Check if user has specified a valid directory
    directory = self.check_directory(self.ui.t2t6LE_1.text())
    if directory == None: 
        self.ui.Console.setPlainText('Invalid directory selected')
        return

    T1 = self.ui.t2t6SB_1.value()
    T2 = self.ui.t2t6SB_2.value()
    Increments = self.ui.t2t6SB_3.value()
    temps = [x for x in range(T1, T2 + Increments, Increments)]
    vibrational_factor = self.ui.t2t6dsb1.value()
    pressure_factor = self.ui.t2t6dsb2.value()

    Files = [f"{directory}/{x}" for x in os.listdir(directory) if x[-4:] in ['.log','.out']]
    self.ui.Console.setPlainText(f'Starting analysis on {len(Files)} files.')
    Cinfo=''
    Ping = time.time()
    all_data = np.empty((8,))
    for index, File in enumerate(Files):
        if time.time()-Ping > 1.0: #only update once a second
            self.ui.progressBar.setValue(int((index)/len(Files)*100))
            Ping = time.time()
        # Read File Data
        qc = QCData(File)
        Data = []
        for T in temps:
            Data.append(thermochemistry(
                qc,
                T,
                pressure=(101325 * pressure_factor),
                scale_factor=vibrational_factor
            ))
        extracted_data = get_thermos(Data)
        all_data = np.vstack((all_data,extracted_data))
    self.ui.progressBar.setValue(0)
    Cinfo='Finished analysis on all files.'
    self.ui.Console.setPlainText(Cinfo)
    all_data = np.delete(all_data,0,axis=0)
    np.savetxt(f"{directory}/Summary.csv",all_data,delimiter=',',header=','.join(fields),fmt="%.6f")