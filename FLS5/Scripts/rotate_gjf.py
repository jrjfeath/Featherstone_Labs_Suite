import os
import time

from math import sin,cos,pi,sqrt
from shutil import copyfile

def rotate_gjf(self):
    File = self.ui.t2t4LE_1.text()
    if os.path.isfile(File) == True: #If File exists
        directory = File[:-4]+'_Steps'
        if not os.path.exists(directory): #check to see if subfolder exists
            os.makedirs(directory) #if it does not make it 
        rotate(self,File,directory)
    else:
        self.ui.Console.setPlainText('The File path was left empty.')

def rotate(self,File,directory):
    opf = open(File,'r')
    lines = opf.readlines()
    opf.close()
    geometry=[] #Get geometry of atoms from File
    for line in range(len(lines)): #for each line in File
        try: #see if the line matches xyz
            if lines[line].split()[0].isalpha() == True and len(lines[line].split()[0]) < 3:
                if geometry == []: #If geometry is empty this is where xyz begins
                    startgeom = line
                geometry.append(lines[line].split())
        except IndexError:
            pass
    if len(geometry) == 0: #if no geometry is found
        self.ui.Console.setPlainText('The File specified does not contain valid xyz coordinates.')
        return #exit the function
    copyfile(File, os.path.join(directory,'Rotation_1.gjf'))
    rotaxis = self.ui.t2t4CB_1.currentIndex() #0 = X, 1 = Y, 2 = Z
    angle = self.ui.t2t4SB_1.value() #Obtain rotation angle
    #Default Variables
    angle1 = 0 #starting angle
    num = 360 #There are 360 degrees
    n = 2 #Start at 2 because provided File is step 1
    rounds = num/angle
    vector = [0,0,0]
    #Possible axis to rotate, DO NOT CHANGE!
    if rotaxis == 2:
        axis = [0,0,0.1]
    if rotaxis == 1:
        axis = [0,0.1,0]
    if rotaxis == 0:
        axis = [0.1,0,0]
    Ping = time.time()
    while n <= rounds:
        if time.time()-Ping > 0.1:
            self.ui.progressBar.setValue((n/rounds)*100)
            Ping = time.time()
        #Angle calculation
        angle1 = angle1+angle
        theta = angle1 * pi/180
        String = ''.join(lines[0:int(startgeom)])
        for i in geometry:
            # This is molecule geometry
            point = [float(i[1]),float(i[2]),float(i[3])] 
            #Specifying all the points required for calculation
            a = vector[0]                                  
            b = vector[1]                                           
            c = vector[2]                                          
            u = axis[0]  
            v = axis[1] 
            w = axis[2]
            x = point[0]
            y = point[1]
            z = point[2]
            L = u*u +v*v + w*w
            #X, Y, Z calkulations #noonewillseethis #shhhhhhhhh #howareyouseeingthis?
            X = ((a*(v*v+w*w)-u*(b*v+c*w-u*x-v*y-w*z))*(1-cos(theta))+L*x*cos(theta)+sqrt(L)*(c*v+b*w-w*y+v*z)*sin(theta))/float(L)
            Y = ((b*(u*u+w*w)-v*(a*u+c*w-u*x-v*y-w*z))*(1-cos(theta))+L*y*cos(theta)+sqrt(L)*(c*u-a*w+w*x-u*z)*sin(theta))/float(L)
            Z = ((c*(v*v+u*u)-w*(a*u+b*v-u*x-v*y-w*z))*(1-cos(theta))+L*z*cos(theta)+sqrt(L)*(-b*u+a*v-v*x+u*y)*sin(theta))/float(L) 
            String += (' %s    %.8f    %.8f    %.8f\n' % (i[0],X,Y,Z))
        String+=''.join(lines[int(startgeom)+len(geometry):])
        opf = open(os.path.join(directory,'Rotation_'+str(n)+'.gjf'), 'w')
        opf.write(String)
        opf.close()
        num = num - angle
        n +=1
    self.ui.progressBar.setValue(0)
    self.ui.Console.setPlainText('The rotation process has completed.\nFiles have been written to:\n'+directory)
