import copy
import os
import re
import sys
import time

import numpy as np

from math import pi, log, exp

#http://web.utk.edu/~rcompton/constants
#J = kgm2s-2
h = 6.6260755*(10**-34) #Js
kb = 1.380662*(10**-23) #JK-1
Na = 6.0221367*(10**23) #mol-1
kjth = 3.8088*(10**-4) #kj/mol to hartree
amutkg = 1.66054*(10**-27) #convert amu to kg
atmt = 101325 #convert atm to pascal
atm = 10**-20 #angstrom^2 to meter^2
R = 8.31446261815324 #JK-1mol-1
c = 299792458 #m/s

def analyze_temperature(self):

    #Check if user has specified a valid directory
    directory = self.check_directory(self.ui.t2t6LE_1.text())
    if directory == None: 
        self.ui.Console.setPlainText('Invalid directory selected')
        return

    T1 = self.ui.t2t6SB_1.value()
    T2 = self.ui.t2t6SB_2.value()
    Increments = self.ui.t2t6SB_3.value()
    vibrational_factor = self.ui.t2t6dsb1.value()
    pressure = self.ui.t2t6dsb2.value()
    use_imaginaries = self.ui.t2t6CB_1.currentIndex()

    def calculate_energy(File):
        with open(File,'r') as opf:
            Data = opf.read()

        thermo = re.findall(r'Thermochemistry(.*?) -',Data)
        if len(thermo) == 0: #no thermochemistry skip file
            return {}

        rsn = re.findall(r'Rotational symmetry number(.*?)\.',Data) #rotational symmetry number
        mass = float(re.findall(r'Molecular mass:(.*?)\.',Data)[0])*amutkg #find mass and convert to kg
        if pressure == 1.0:
            P = float(re.findall(r'Pressure(.*?) Atm',Data)[0])*atmt #find pressure and convert to kg
        else:
            P = pressure*atmt
        rot_temp =  re.findall(r'\(Kelvin\) ([\s\S]*?) Rotational',Data)
        vib_temp = re.findall(r'Vibrational temperatures:([\s\S]*?)Zero-point',Data)
        try: SPE = float(re.findall(r'SCF Done: (.*?) A\.U\.',Data)[-1].split()[-1])
        except IndexError: SPE = float(re.findall(r'[\|\\]H\s*F\s*=\s*([\s\S]*?)[\|\\]',Data)[0].replace('\n','').replace(' ',''))
        #User can restart job and lose charge/multiplicity block in beginning of log
        multiplicity = re.findall(r'cartesian basis functions\n(.*?) beta electrons',Data)
        try:
            multiplicity = re.findall(r"[-+]?\d*\.\d+|\d+",multiplicity[0])
            multiplicity = int(multiplicity[0])-int(multiplicity[1])+1
        except IndexError:
            multiplicity = 1

        #If molecule is actually an atom there will be no rot/vib temps or symmetry number
        if len(rot_temp) > 0: 
            rot_temp = re.findall(r"[-+]?\d*\.\d+|\d+",rot_temp[0])
            rot_temp = [float(x) for x in rot_temp]
            rsn = int(rsn[0])
        else: rot_temp = []

        if len(vib_temp) > 0: 
            vib_temp = re.findall(r"[-+]?\d*\.\d+|\d+",vib_temp[0])
            #Remove vibrational temps below 0K as per gaussian instructions, pg 7.
            vib_temp = [float(x)*vibrational_factor for x in vib_temp if float(x) > 0]

        if use_imaginaries == 1: #If user has selected to use negatives
            Harmonic = re.findall(r'Frequencies --(.*?)-------------------',Data,re.DOTALL)[-1]
            Harmonic = Harmonic.split('\n')
            Harmonic[0] = 'Frequencies --'+Harmonic[0]
            vib_temp = [] #Harmonic value
            
            for line in Harmonic:
                if 'Frequencies' in line:
                    line = line.split()[2:]
                    for v in line:
                        vib_temp.append(round(abs(((float(v)*h)/kb)*c*100),2))

        #All math per: https://gaussian.com/wp-content/uploads/dl/thermo.pdf

        def translational(mass,T,P):
            '''Calculate translation contributions, per explanation on page 3-4.'''
            qt = (((2*pi*mass*kb*T)/h**2)**(3/2))*(kb*T)/P #unitless
            St = R*(log(qt)+2.5) #JK-1mol-1
            Et = (1.5*R*T) #Jmol-1
            Ct = 1.5*R #JK-1mol-1
            return St, Et, Ct

        def rotational(T,rsn,rot_temp):
            '''Calculate rotational contributions, per explanation on page 4-6.'''
            if len(rot_temp) == 0: #If it is an atom 
                Sr = 0 #JK-1mol-1
                Er = 0 #Jmol-1
                Cr = 0 #JK-1mol-1
            if len(rot_temp) == 1: #If molecule is linear
                qr = (1/rsn)*(T/rot_temp[0])
                Sr = R*(log(qr)+1) #JK-1mol-1
                Er = R*T #Jmol-1
                Cr = R #JK-1mol-1
            if len(rot_temp) > 1: #If molecule is non-linear
                rot_temp = np.prod(rot_temp) #get product of rotational temps
                qr = (pi**0.5/rsn)*(T**1.5/rot_temp**0.5)
                Sr = R*(log(qr)+1.5) #JK-1mol-1
                Er = 1.5*R*T #Jmol-1
                Cr = 1.5*R #JK-1mol-1
            return Sr, Er, Cr

        def vibrational(T,vib_temp):
            '''Calculate vibrational contributions, per explanation on page 6-7.'''
            Sv = R*sum([(x/(exp(x)-1))-log(1-exp(-x)) for x in vib_temp]) #JK-1mol-1
            Ev = R*sum([x*T*(0.5+(1/(exp(x)-1))) for x in vib_temp]) #Jmol-1
            Cv = R*sum([exp(x)*(x/(exp(-x)-1))**2 for x in vib_temp]) #JK-1mol-1
            return Sv, Ev, Cv

        def electronic(multiplicity):
            '''Calculate electronic contributions, per explanation on page 4.'''
            Se = R*(log(multiplicity)) #JK-1mol-1
            return Se

        Energies = {}
        for T in range(T1,T2+1,Increments):
            St,Sr,Se,Sv = 0,0,0,0
            Et,Er,Ev = 0,0,0
            Ct,Cr,Cv = 0,0,0
            St,Et,Ct = translational(mass,T,P)
            Sr,Er,Cr = rotational(T,rsn,rot_temp)
            if multiplicity != 1:
                Se = electronic(multiplicity)
            if len(vib_temp) > 0:
                tvib_temp = [x/T for x in copy.deepcopy(vib_temp) if x]
                Sv,Ev,Cv = vibrational(T,tvib_temp)
            Stot = (St+Sr+Se+Sv)
            #print('Filename,Entropy(E),Entropy(T),Entropy(R),Entropy(V),Stot')
            #print('%s,%.3f,%.3f,%.3f,%.3f,%.3f'%(os.path.basename(File),Se/4.184,St/4.184,Sr/4.184,Sv/4.184,Stot/4.184))
            Etot = (Et+Er+Ev)
            #print('Filename,Energy(T),Energy(R),Energy(V),Etot')
            #print('%s,%.3f,%.3f,%.3f,%.3f'%(os.path.basename(File),Et/4.184/1000,Er/4.184/1000,Ev/4.184/1000,Etot/4.184/1000))
            _ = (Cv+Ct+Cr) #Might eventually find a use for these
            Hcorr = Etot+(R*T)
            Gcorr = Hcorr-(T*(Stot))
            Energies[T] = [Stot,SPE,SPE+Hcorr/1000*kjth,SPE+Gcorr/1000*kjth]
            #print(Etot,Hcorr,Gcorr)
            #print('Hcorr,Gcorr,Gibbs')
            #print('%s,%.6f,%.6f,%.6f'%(os.path.basename(File),Hcorr/1000*kjth,Gcorr/1000*kjth,SPE+Gcorr/1000*kjth))
            #print(SPE+Hcorr/1000*kjth,SPE+Gcorr/1000*kjth)
        
        return Energies

    Files = [directory+'/'+x for x in os.listdir(directory) if x.endswith('.log')]
    self.ui.Console.setPlainText(f'Starting analysis on {len(Files)} files.')
    Cinfo=''
    string = 'Filename,Temperature,Entropy,HF,Enthalpy,Free Energy\n'
    Ping = time.time()
    for index, File in enumerate(Files):
        if time.time()-Ping > 1.0: #only update once a second
            self.ui.progressBar.setValue(int((index)/len(Files)*100))
            Ping = time.time()
        Data = calculate_energy(File)
        if len(Data) == 0:
            Cinfo+=f'No thermochemical data found in {File}'
        for key in Data:
            #Filename,Entropy,HF,Enthalpy,Free Energy
            string += f'{os.path.basename(File)},{key},{Data[key][0]},{Data[key][1]},{Data[key][2]},{Data[key][3]}\n'
    self.ui.progressBar.setValue(0)
    Cinfo='Finished analysis on all files.'
    self.ui.Console.setPlainText(Cinfo)

    with open(directory+'/summary.csv','w') as opf:
        opf.write(string)
