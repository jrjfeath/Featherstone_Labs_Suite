import os
import re

import xlsxwriter

from Scripts.SPE import check_file_closed

def spectrum(self):
    directory = self.check_directory(self.ui.t2t3LE_1.text())
    if directory:
        log_files = [os.path.join(directory,f) for f in os.listdir(directory) if f.lower().endswith('.log') or f.lower().endswith('.out')] #Get logs in directory 
        freqmin = self.ui.t2t3SB_2.value()
        freqmax = self.ui.t2t3SB_3.value()
        HWHM = self.ui.t2t3SB_4.value()
        stepsize = self.ui.t2t3SB_1.value()
        log_type = self.ui.t2t3CB_1.currentText()
        relative = self.ui.t2t3CB_2.currentIndex()
        v_range = [freqmin+x*stepsize for x in range(int(((freqmax-freqmin)/stepsize)+1))]
        if len(log_files) > 0:
            if log_type == 'Harmonic':
                Extract_Harmonic(self,directory,log_files,freqmin,freqmax,HWHM,stepsize,relative,v_range)
            else:
                Extract_Anharmonic(self,directory,log_files,freqmin,freqmax,HWHM,stepsize,relative,v_range)
        else:
            self.ui.Console.setPlainText('No log files in specified directory.')
    else:
        self.ui.Console.setPlainText('Invalid directory')
        
def Extract_Anharmonic(self,directory,log_files,freqmin,freqmax,HWHM,stepsize, relative,v_range):
    console_info = 'Beginning process, '+str(len(log_files))+' files to analyze.\n'
    self.ui.Console.setPlainText(console_info)  
    xlsxname = check_file_closed(os.path.join(directory,'Spectra'),'.xlsx')
    workbook=xlsxwriter.Workbook(xlsxname)
    i = 0
    for file in log_files: #Run process for each log
        self.ui.progressBar.setValue(int(((i+1)/len(log_files))*100))
        filename = os.path.basename(file)[:-4]
        
        #Set empty lists for harmonic and anharmonic values
        HF=[]
        HI=[]
        AF=[]
        AI=[]

        #Open file and retrieve text
        openfreq=open(file,'r') 
        text=openfreq.read()
        openfreq.close()

        #Search for the frequency data, it is the second index for the following search term
        try:
            Data = re.findall(r'Fundamental Bands(.*?)Overtones',text,re.DOTALL)[-1]
            Data = Data.replace('-','').strip().split('\n')
            
            if len(filename) < 30:
                filename = filename.translate({ord(c): None for c in '[]:*?/\!@#$'})
            else: #excel sheet names must be under 30 characters long
                filename = filename[0:29].translate({ord(c): None for c in '[]:*?/\!@#$'})
            worksheet = workbook.add_worksheet(filename)
            worksheet.write('G1','Anharmonic Stick')
            worksheet.write('G2','E(harm)')
            worksheet.write('H2','E(anharm)')
            worksheet.write('I2','I(harm)')
            worksheet.write('J2','I(anharm)')

            line_index=2
            for line in Data[1:]: #For each line split the line and append to list
                line = line.split()
                if '*' in line[3]: #If the calculation spits a null value set it to 0 for intensity
                    line[3] = 0.0
                if '*' in line[4]:
                    line[4] = 0.0
                HF.append(float(line[1]))
                worksheet.write(line_index,6,float(line[1]))
                HI.append(float(line[3]))
                worksheet.write(line_index,7,float(line[2]))
                AF.append(float(line[2]))
                worksheet.write(line_index,8,float(line[3]))
                AI.append(float(line[4]))
                worksheet.write(line_index,9,float(line[4])) 
                line_index+=1

            Harmonic = re.findall(r'Frequencies --(.*?)-------------------',text,re.DOTALL)[-1]
            Harmonic = Harmonic.split('\n')
            Harmonic[0] = 'Frequencies --'+Harmonic[0]
            HV = [] #Harmonic value
            HVI = [] #Harmonic value intensity
            
            for line in Harmonic:
                if 'Frequencies' in line:
                    line = line.split()[2:]
                    for v in line:
                        HV.append(float(v))   
                elif 'IR' in line:
                    line = line.split()[3:]
                    for inten in line:
                        HVI.append(float(inten))

            worksheet.write('O1','Harmonic Stick')
            worksheet.write('O2','Wavenumber')
            worksheet.write('P2','Intensity')
            line_index=2
            for index in range(len(HV)):
                worksheet.write(line_index,14,HV[index])
                worksheet.write(line_index,15,HVI[index])
                line_index+=1
                        
        except IndexError:
            HF = []

        if len(HF) == 0: #If HF data is found in the file
            console_info += filename+' does not contain any usable freqency data.\n'
            self.ui.Console.setPlainText(console_info)
            return

        #Harmonic values 
        worksheet.write('A1','Harmonic Gaussian, E(harm)')
        worksheet.write('A2','Wavenumber')
        worksheet.write('B2','Intensity')

        HI_range = [0 for x in range(len(v_range))] #Set the intensities to 0 each run
        for v_index in range(len(HF)): #for values in HF
            for v in range(round(HF[v_index])-300,round(HF[v_index])+300): #for values in
                if v in v_range: #If value is in the range then calculate intensity
                    HI_range[v_range.index(v)] += (1/(1+((v-HF[v_index])/HWHM)**2)*float(HI[v_index]))

        if relative == 0:
            worksheet.write('B2','Relative Intensity')
            HI_range[:] = ['%3f' % (x/max(HI_range)) for x in HI_range] #Make all values relative

        #Anharmonic values
        worksheet.write('D1','Anharmonic Gaussian, E(harm)')
        worksheet.write('D2','Wavenumber')
        worksheet.write('E2','Intensity')

        AI_range = [0 for x in range(len(v_range))] #Set the intensities to 0 each run
        for v_index in range(len(AF)): #for values in HF
            for v in range(round(AF[v_index])-300,round(AF[v_index])+300): #for values in
                if v in v_range: #If value is in the range then calculate intensity
                    AI_range[v_range.index(v)] += (1/(1+((v-AF[v_index])/HWHM)**2)*float(AI[v_index]))

        if relative == 0:
            worksheet.write('E2','Relative Intensity')
            AI_range[:] = ['%3f' % (x/max(AI_range)) for x in AI_range] #Make all values relative
        
        #Harmonic values from harmonic stick
        worksheet.write('L1','Harmonic Gaussian (Stick)')
        worksheet.write('L2','Wavenumber')
        worksheet.write('M2','Intensity')

        HSI_range = [0 for x in range(len(v_range))] #Set the intensities to 0 each run
        for v_index in range(len(HV)): #for values in HF
            for v in range(round(HV[v_index])-300,round(HV[v_index])+300): #for values in
                if v in v_range: #If value is in the range then calculate intensity
                    HSI_range[v_range.index(v)] += (1/(1+((v-HV[v_index])/HWHM)**2)*float(HVI[v_index]))

        if relative == 0:
            worksheet.write('M2','Relative Intensity')
            HSI_range[:] = ['%3f' % (x/max(HSI_range)) for x in HSI_range] #Make all values relative

        #Write all data to the excel file
        for v_index in range(len(v_range)):
            worksheet.write(v_index+2,0,v_range[v_index]) #Write wavenumber
            worksheet.write(v_index+2,1,float(HI_range[v_index])) #Write intensity harmonic
            worksheet.write(v_index+2,3,v_range[v_index]) #Write wavenumber
            worksheet.write(v_index+2,4,float(AI_range[v_index])) #Write intensity harmonic
            worksheet.write(v_index+2,11,v_range[v_index]) #Write wavenumber
            worksheet.write(v_index+2,12,float(HSI_range[v_index])) #Write harmonic intensity from harmonic stick
        i+=1 
    workbook.close()
    console_info += 'Process completed'
    self.ui.Console.setPlainText(console_info)  
    self.ui.progressBar.setValue(0)

def Extract_Harmonic(self,directory,log_files,freqmin,freqmax,HWHM,stepsize,relative,v_range): #Generate Spectra 
    #Empty lists for storing 
    freq_master = []
    inten_master = []
    energy_master = []
    file_master = []
    i=0
    console_info = 'Beginning process, '+str(len(log_files))+' files to analyze.\n'
    self.ui.Console.setPlainText(console_info)  
    for file in log_files: #Run process for each log
        self.ui.progressBar.setValue(int((i+1)/len(log_files))*100) #Set run number to value *2 of total logs
        freq=[]
        inten=[]
        ZPE_correct = ''
        energy = ''
        openfreq=open(file,'r') #Open file and retrieve lines
        lines=openfreq.readlines()
        openfreq.close()  
        if file.endswith('.log'):
            for line in lines:
                if 'Frequencies --' in line: #Get frequency data
                    x=str(line)[15::].split()
                    for item in x:
                        item = float(item)
                        freq.append(item)
                elif 'IR Inten    --' in line: #Get ir intensity data
                    y=(str(line)[15::]).split()
                    for item in y:
                        item = float(item)                         
                        inten.append(item)
                elif 'Zero-point correction=' in line:
                    ZPE_correct = line.split()[2]
                elif 'SCF Done:' in line:
                    energy = line.split()[4]
            if ZPE_correct and energy and len(freq) > 0:
                if relative == 0:
                    inten[:] = ['%3f' % (x/max(inten)) for x in inten]
                inten_master.append(inten)
                freq_master.append(freq)
                energy_master.append(float(energy)+float(ZPE_correct))
                file_master.append(file)
            else:
                console_info += os.path.basename(file)+' does not contain any usable freqency data.\n'
            i+=1
        elif file.endswith('.out'):
            start = 0
            end = 0
            for x in range (len(lines)):
                if "IR SPECTRUM" in lines[x]:
                    start = x
                if "* The epsilon (eps) is given for a Dirac delta lineshape." in lines[x]:
                    end = x    
            raw_spec = lines[start+6:end-1]
            for row in range(len(raw_spec)):
                temp = raw_spec[row].split()
                freq.append(temp[1])
                inten.append(temp[3])
            if len(freq) != 0:
                freq_master.append(freq)
                inten_master.append(inten)
                energy_master.append(0)
                file_master.append(file)
            else:
                console_info += os.path.basename(file)+' does not contain any usable freqency data.\n'
    if len(freq_master) == 0: #If no frequency files found ditch process
        console_info += 'Process aborted, no frequency files found.'
        self.ui.Console.setPlainText(console_info)
        return
    energy_master, freq_master, inten_master, file_master = zip(*sorted(zip(energy_master, freq_master, inten_master, file_master)))
    console_info += 'Writing data for '+str(len(energy_master))+' logs to '+os.path.join(directory,'Spectra.xlsx')+'.\n'
    self.ui.Console.setPlainText(console_info)  
    xlsxname = check_file_closed(os.path.join(directory,'Spectra'),'.xlsx')
    workbook=xlsxwriter.Workbook(xlsxname)
    i=0
    for energies in range(len(energy_master)):
        self.ui.progressBar.setValue(int((i+1)/len(energy_master))*100)
        filename = os.path.basename(file_master[energies])[:-4]
        if len(filename) < 30:
            filename = filename.translate({ord(c): None for c in '[]:*?/\!@#$'})
        else: #excel sheet names must be under 30 characters long
            filename = filename[0:29].translate({ord(c): None for c in '[]:*?/\!@#$'})
        worksheet = workbook.add_worksheet(filename)
        worksheet.write('A1','Wavenumber')
        worksheet.write('B1','Relative Intensity')

        i_range = [0 for x in range(int(freqmax/stepsize)+1)] #Set the intensities to 0 each run

        for freqs in range(len(freq_master[energies])):
            for wavenumber_in in range(round(float(freq_master[energies][freqs]))-300,round(float(freq_master[energies][freqs]))+300):
                if wavenumber_in in v_range:
                    i_range[v_range.index(wavenumber_in)] += (1/(1+((wavenumber_in-float(freq_master[energies][freqs]))/HWHM)**2)*float(inten_master[energies][freqs]))

        if relative == 0:
            i_range[:] = ['%3f' % (x/max(i_range)) for x in i_range] #Make all values relative

        for frequencies in range(len(v_range)):
            worksheet.write(frequencies+1,0,v_range[frequencies])
            worksheet.write(frequencies+1,1,float(i_range[frequencies])) 
        i+=1
    workbook.close()
    console_info += 'Process completed'
    self.ui.Console.setPlainText(console_info)  
    self.ui.progressBar.setValue(0)
