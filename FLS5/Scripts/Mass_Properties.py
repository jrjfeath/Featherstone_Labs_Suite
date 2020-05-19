import os
import re
import sys
import time

from math import sqrt

import numpy as np

from Atom_Info import chemical_symbols, atomic_masses_legacy
from SPE import check_file_closed

def Mass_Props(self):
	directory = self.check_directory(self.ui.t2t5LE_1.text())
	if directory == None:
		self.ui.Console.setPlainText('Invalid directory')
		return
	if self.ui.t2t5CB_1.currentIndex() == 0:
		extension = '.gjf'
	else:
		extension = '.log'
	files = [os.path.join(directory,f) for f in os.listdir(directory) if f.lower().endswith(extension)]
	if len(files) > 0:
		extract(self,extension,files,directory)
	else:
		self.ui.Console.setPlainText('No files found in specified directory.')
	
def find_float(self,list):
	fv = []
	for i in list:
		try:
			fv.append(float(i))
		except ValueError:
			pass
	return fv

def extract(self,extension,files,directory):
	status = self.ui.t2t5CB_2.currentIndex() #Check if user wants to use failed log files
	CInfo = 'Starting extraction process.\n'
	self.ui.Console.setPlainText(CInfo)
	file_number = 0
	geometry_array = []
	filename = []
	Ping = time.time()
	for file in files:
		if time.time() - Ping > 0.1:
			self.ui.progressBar.setValue(file_number/len(files)*100)
			Ping = time.time()
		opf = open(file,'r')
		data = opf.read()
		opf.close()
		
		if extension == '.gjf':
			data = (data.split('\n'))
			n = 0
			geom_index = []
			for line in data:
				split_line = line.split() #Split line
				if len(split_line) == 4: #If line breaks into four sections
					if '.' in split_line[1] and '.' in split_line[2] and '.' in split_line[3]: #if it fits geometry
						geom_index.append(n)#write the index
				n+=1
			data = data[geom_index[0]:geom_index[-1]+1]
			for lines in range(len(data)):
				line = data[lines].split()
				data[lines] = str(lines+1)+' '+str(chemical_symbols.index(line[0]))+' 0 '+str(float(line[1]))+' '+str(float(line[2]))+' '+str(float(line[3]))
			GEOM = data
			ESP = [1] #Write default value as ESP not found in inputs
		
		else: #If the user is using log files
			data = data.replace('\n','ggez') 
			
			if 'Normal termination' in data and status == 0: #If user wants to use good files
				pass
			elif status == 1: #If user wants to use all log files
				pass
			else: #If it does not meet either skip this file
				break
			
			try: CSA = re.findall(r'Cavity surface area(.*?)ggez',data)[-1].split()
			except IndexError: CSA = [0]

			try: CV = re.findall(r'Cavity volume(.*?)ggez',data)[-1].split()
			except IndexError: CV = [0]

			try: RC_INFO = re.findall(r'Rotational constants(.*?)ggez',data)[-1].split()
			except IndexError: RC_INFO = [0,0,0]

			try: DM_INFO = re.findall(r'Dipole moment(.*?)Quadrupole moment',data)[-1].replace('ggez','').split()
			except IndexError: DM_INFO = [0,0,0,0]

			try: QM_INFO = re.findall(r'Quadrupole moment(.*?)Traceless Quadrupole',data)[-1].replace('ggez','').split()
			except IndexError: QM_INFO = [0,0,0,0,0,0]

			try: GEOM = re.findall(r'Standard orientation(.*?)Rotational constants',data)[-1].split('ggez')[5:-2]
			except IndexError: GEOM = [[0,0,0,0,0,0]]
			
			try: ESP = re.findall(r'ESP charges:(.*?)Sum of ESP charges =',data)[-1].split('ggez')[2:-1]
			except IndexError: ESP = ['0 0 0']
			ESP = [float(x.split()[2]) for x in ESP]

			data = data.replace('ggez','')
			data = data.replace('\r','')
			try: Polar = re.findall(r'P\s*o\s*l\s*a\s*r\s*=\s*(.*?)[\|\\]',data)[-1].replace(' ','').split()
			except IndexError: Polar,ESP = [[0,0,0,0,0,0]],[1]
			
			try: Hyper = re.findall(r'H\s*y\s*p\s*e\s*r\s*P\s*o\s*l\s*a\s*r\s*=\s*(.*?)[\|\\]',data)[-1].replace(' ','').split()
			except IndexError: Hyper,ESP = [[0,0,0,0,0,0,0,0,0,0]],[1]		

			CSA = find_float(self,CSA)
			CV = find_float(self,CV)
			RC_INFO = find_float(self,RC_INFO)
			DM_INFO = find_float(self,DM_INFO)
			QM_INFO = find_float(self,QM_INFO)
		
		xt, yt, zt = 0,0,0
		for i in GEOM:
			i = i.split()
			xt+=float(i[3])
			yt+=float(i[4])
			zt+=float(i[5])
		xt = xt/len(GEOM)
		yt = yt/len(GEOM)
		zt = zt/len(GEOM)

		MT = 0.0
		lines = []
		geometry = []
		n = 0
		for i in GEOM:
			i = i.split()
			COM = [float(i[3])-xt,float(i[4])-yt,float(i[5])-zt]
			RCoM = sqrt(COM[0]**2+COM[1]**2+COM[2]**2)
			Mass = atomic_masses_legacy[int(i[1])]
			MT += Mass
			if len(ESP) != 1: #If ESP found in log
				line = i[1],i[3],i[4],i[5],RCoM,ESP[n],ESP[n]*RCoM
				n+=1
			else:
				line = i[1],i[3],i[4],i[5],RCoM,Mass,RCoM*Mass
			lines.append(line)
		lines = sorted(lines, key=lambda x : x[6])

		try:
			if len(ESP) != 1: #If ESP found in log
				opf = open(file[:-4]+'_ESP_Geometry_Data.csv','w')
				opf.write('Atomic Number,X,Y,Z,RCoM,ESP,ESP*RCoM\n')
				for i in lines:
					opf.write('%s,%s,%s,%s,%f,%f,%f\n'%(i))
					geometry.append(float(i[-1]))	
			else:
				opf = open(file[:-4]+'_Mass_Geometry_Data.csv','w')
				opf.write('Atomic Number,X,Y,Z,RCoM,Atomic Mass,Mass*RCoM\n')
				for i in lines:
					opf.write('%s,%s,%s,%s,%f,%f,%f\n'%(i))
					geometry.append(float(i[-1]))	
			opf.write('COM:,'+str(xt)+','+str(yt)+','+str(zt)+'\n')				
			opf.close()
			geometry_array.append(geometry)
			filename.append(file[file.rfind('\\')+1:])
		except PermissionError:
			CInfo += ("Cannot write to "+str(os.path.basename(file)[:-4])+"_Geometry.csv\n")			

		if extension == '.log':
			if len(ESP) != 1: #If ESP found in log
				csvname = check_file_closed(file[:-4]+'_ESP_Parameters','.csv')
				opf = open(csvname,'w')
				opf.write('%s,%s\n'%('Polarization',Polar[0]))
				opf.write('%s,%s\n'%('Hyper Polarization',Hyper[0]))
				opf.close()
			else:
				String ='%s,%s\n'%('Cavity surface area',CSA[0])
				String+='%s,%s\n'%('Cavity Volume',CV[0])
				String+='%s,%s\n'%('Dipole Moment X',DM_INFO[0])
				String+='%s,%s\n'%('Dipole Moment Y',DM_INFO[1])
				String+='%s,%s\n'%('Dipole Moment Z',DM_INFO[2])
				String+='%s,%s\n'%('Dipole Moment Tot',DM_INFO[3])
				String+='%s,%s\n'%('Quadrupole Moment XX',QM_INFO[0])
				String+='%s,%s\n'%('Quadrupole Moment YY',QM_INFO[1])
				String+='%s,%s\n'%('Quadrupole Moment ZZ',QM_INFO[2])
				String+='%s,%s\n'%('Quadrupole Moment XY',QM_INFO[3])
				String+='%s,%s\n'%('Quadrupole Moment XZ',QM_INFO[4])
				String+='%s,%s\n'%('Quadrupole Moment YZ',QM_INFO[5])
				String+='%s,%s\n'%('Nominal Mass',MT)
				String+='%s,%s\n'%('Rotational Constant A',RC_INFO[0])
				String+='%s,%s\n'%('Rotational Constant B',RC_INFO[1])
				String+='%s,%s\n'%('Rotational Constant C',RC_INFO[2])
				csvname = check_file_closed(file[:-4]+'_Mass_Parameters','.csv')
				opf = open(csvname,'w')
				opf.write(String)
				opf.close()
		file_number+=1
	#Tell user that files have been analyzed and starting coordinate list
	CInfo += str(file_number)+' files analyzed, proceeding to make coordinate lists.\n'
	self.ui.progressBar.setValue(0)
	self.ui.Console.setPlainText(CInfo)
	
	maxlength = max(len(s) for s in geometry_array)
	leading_zeroes = []
	trailing_zeroes = []
	n=0
	for geometry in geometry_array:
		leading = geometry
		trailing = geometry
		while len(trailing) != maxlength:
			leading = [0.0]+leading
			trailing.append(0.0)
		leading_zeroes.append(leading)
		trailing_zeroes.append(trailing)
		n+=1
	CInfo += 'Writing coordinate lists to respective files.\n'
	self.ui.Console.setPlainText(CInfo)

	if len(ESP) != 1: #If ESP found in log
		Tname = check_file_closed(os.path.join(directory,'ESP_Trailing_Coordinate_List'),'.csv')
		T_coordinate = open(Tname,'w')
		Lname = check_file_closed(os.path.join(directory,'ESP_Leading_Coordinate_List'),'.csv')
		L_coordinate = open(Lname,'w')
	else:
		Tname = check_file_closed(os.path.join(directory,'Mass_Trailing_Coordinate_List'),'.csv')
		T_coordinate = open(Tname,'w')
		Lname = check_file_closed(os.path.join(directory,'Mass_Leading_Coordinate_List'),'.csv')
		L_coordinate = open(Lname,'w')
	#Make a string of names
	names = ''
	for name in filename: names += name+','
	names = names[:-1]+'\n'
	T_coordinate.write(names)
	L_coordinate.write(names)
	#Make a string of coordinates
	Ping = time.time()
	for i in range(maxlength):
		if time.time()-Ping > 0.1:
			self.ui.progressBar.setValue((i/maxlength)*100)
			Ping = time.time()
		leading = ''
		trailing = ''
		for index in trailing_zeroes:
			trailing += str(index[i])+','
		for index in leading_zeroes:
			leading += str(index[i])+','
		T_coordinate.write(trailing[:-1]+'\n')
		L_coordinate.write(leading[:-1]+'\n')

	CInfo += 'Process completed!'
	self.ui.progressBar.setValue(0)
	self.ui.Console.setPlainText(CInfo)
