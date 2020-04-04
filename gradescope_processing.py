"""
File: GRADESCOPE_PROCESSING.PY
Author: Patrick McNamee
Date: April 4 2020
Python: Version 3.5 or sooner (requirement from subprocess library)

Description:
Python script to take a downloaded zip file from gradescope and change pdf names to students' first and last names.

Python Libraries:
glob         -- reads the files in directory
os           -- used for moving paths
subprocesses -- used to generate the Unix commands

Unix tools:
pdftotext -- takes a pdf and outputs a text file

Edits:
"""

import os
import glob
import subprocess

#Interesting stack overflow solution
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)
    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)
    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

with cd("~/Downloads"):
    #unzip file and move in
    subprocess.run(['unzip', 'submissions.zip'])
    assignment_folder = glob.glob("./assignment_*")[0]
    with cd(assignment_folder):
        #get all pdf files which are the students' results
        files = glob.glob("./*.pdf")
        for f in files:
            #Get the text output 
            subprocess.run(['pdftotext', f, f[:-4] + '.txt'])
            with open(f[:-4] + '.txt' , 'r') as txt:
                txt.readline() #Class number and assignment name
                name = txt.readline()
            name = name[:-1]
            name = name.split(' ')
            name = '_'.join(name)
            #rename the file
            subprocess.run(['mv', f, name + '.pdf'])
        #cleanup
        subprocess.run(['rm'] + glob.glob('./*.txt'))
        subprocess.run(['ls'])
