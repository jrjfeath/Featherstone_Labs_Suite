# Feather_Labs_Suite
A suite of tools coded for python versions 3.6+ for analyzing gaussian input and output files.

The various tab features are explained below.
--Modifying Tools--
Modify Input Files:
-Used to edit .gjf files in a directory, the new inputs are written to a sub folder as to not overwrite orginal files.
-Pulls defaults from preferences tab. 
-For rwf, scr, and chk options you can select to run with the following options:
  1. Save none of these files (do not save)
  2. Write these files to the same directory that the input is submitted in (same)
  3. In the same directory and then deleted once the job finishes (same and nosave)
  4. Write these files to a directory in your /Scratch/$username/X (where X is chk, rwf, or scr) if that is supported.
-Footer info is anything you want appened below the xyz coordinates. This is generally additional basis set information grabbed from https://www.basissetexchange.org/
-You can select to keep the footer information already present in the input file, i.e connectivity, and append new footer data after this chunk (append) or overwrite the data.

Convert Output to Input:
-Used to read gaussian log files and create input files, the new files are written to a sub folder.
-See above for explanation of rwf,scr, and chk options.

Bulk Rename Files:
-A simple tool for renaming file quickly, not very complex, options are explained on the tab.

--Extraction Tools--
Single Point Energy:
-Simple tool to pull HF or MP2 energies from log file.
-Options are rather straightforward where the user can choose to move all unique files to a sub directory and supress files that have the same name.

Thermochemical Data:
-Extract the thermochemical data of files found in the directory.
-Choose if you want to extract the data of jobs that finished successfully or also extract from failed files.
-Choose how to sort the data in the files, default is by filename
-Choose to show the relative energies based off the lowest sort files by value, disabled when filename selected.

Computed Spectrum:
-Extract a gaussian spectrum based off the frequency data found in the log files provided.
-Step size is the frequency of data points, default is one data point per wavenumber.
-IR-HWHM effects the size of the gaussian peak, do not change this value unless you know what you are doing.
-You can choose to extract harmonic or anharmonic data if it exists in the file. If you run a job that selects for specific anharmonic peaks the resulting spectrum will be a combination of those peaks with the harmonic.

3D Rotation:
-Used to create input files such that you can create a movie of your structure spinning in space in gaussview.
-Rotation axis is not always true depending on how your molecule is oriented, try changing the axis if you don't get what you want.
-Rotation (deg) is how often an input is made, larger values can result in choppier movies.

Geometry and Parameters:
-Extract the geometry data and other various parameters from an optimization. It will arrange your files in a mass weighted spreadsheet with trailing zeroes. 

--Preferences--
-These are where your default parameters are stored. The file storing these parameters can be found in your appdata folder on windows or your home directory in linux.

Please report all bugs and errors under issues or contact me at jrjfeath@uwaterloo.ca
