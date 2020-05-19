import os
import sys
import dropbox

from subprocess import Popen

cwd = os.getcwd()
dd = cwd.replace('\\','/')+'/'
dbx = dropbox.Dropbox('fGuuuA5qQkgAAAAAAABcQuOfMkFHvts0Xz7KdNY4cYwobCjusvCZtO4TJvUxU0I2')

try:
    File = dbx.files_list_folder('/Current').entries
    if os.path.isfile(cwd+r'\McMahon Suite.py'):
        os.remove(cwd+'\McMahon Suite.py')
    dbx.files_download_to_file(dd+File[0].name,File[0].path_lower)
    opf = open(cwd+r'\ID.txt','w')
    opf.write(str(File[0].client_modified))
    opf.close()
except dropbox.exceptions.HttpError as err:
    print('No network connection? Could not download file',err)
    input("Press enter to continue.")

Popen(cwd+'\McMahon Suite.exe', shell=True)
sys.exit()
