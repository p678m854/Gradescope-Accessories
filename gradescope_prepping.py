"""
File: GRADESCOPE_PREPPING.PY
Author: Patrick McNamee
Date: April 3 2020
Python: Version 3.5 or sooner (requirement from subprocess library)

Description:
Python script to take a downloaded zip file and smooth out the irregularities from student submissions in preperation for mass upload to gradescope.

Python Libraries:
glob         -- reads the files in directory
subprocesses -- used to generate the Unix commands
re           -- regex library

Unix tools:
convert -- command from ImageMagic package which is not included as a default in Ubuntu(?)
1) $ sudo apt update
2) $ suod apt-get install imagemagick
Note: There was a weird permission denial when trying to change an image file to a pdf so the next steps are for getting around that
3) $ cd /etc/ImageMagick-6/ (Note: tab complete to ensure you are in the right version)
4) $ sudo nano policy.xml (Note: need the elevated status to edit this file)
5) Comment out the line <policy domain="coder" rights="none" pattern="PDF"> by placing "<!--" in front and "-->" after
6) Write out (Ctrl-o) and exit (Ctrl-x)

To Do:
1) Get rid of the error being thown by mv

Edits:
April 11 2020
-- Added pdf suffix on mv in the renaming of a converted word document
"""

import os
import glob
import re
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
    #Get current downloads
    downloads = glob.glob(pathname="./*")
    subdir = glob.glob("*/")
    #Find all blackboard submission zip files, using regex for matching
    submission_zips = [f for f in downloads
                       if re.findall(r"^./gradebook_[0-9]{4}-[0-9]{5}_", f)]
    #Creating the corresponding submission folder
    submission_folders = ['./' + f.split('_')[2] + '-submissions/' for f in submission_zips]
    for folder in submission_folders:
        if folder not in subdir:
            subprocess.run(["mkdir", folder])
            downloads.append(folder)
        else:
            pass
    #Unzipping submissions and putting them into the appropriate folder
    for comp_file, sub_folder in zip(submission_zips, submission_folders):
        subprocess.run(["unzip", comp_file])
        new_files = [f for f in glob.glob("./*") if f not in downloads and f != sub_folder]
        for nf in new_files:
            subprocess.run(["mv", nf, sub_folder])

        #Going into the submission directory
        with cd(sub_folder):
            assignment_name = sub_folder[2:-1]
            submissions =  glob.glob("./*")
            #Assumes BlackBoard is only one using text files for submissions
            subdetails = [f for f in submissions if f[-4:] == '.txt']
            submissions = [s for s in submissions if s not in subdetails]
            students = [None]*len(subdetails)
            #Create a list of students and associated KU ID
            for i,sub in enumerate(subdetails):
                #Peak at the submission details to get the name and student ID from the first line
                with open(sub, 'r') as file:
                    fst_line = file.readline()
                fst_line = fst_line.split(' ')
                name = '_'.join(fst_line[1:-1])
                ku_id = fst_line[-1][1:9]
                students[i] = (ku_id, name)
            #Go through all students create submission file
            for (ku_id, name) in students:
                #Gathers a student's submission essentially using 
                subs = [f[2:].split('.') for f in submissions if ku_id in f and f[-4:] != '.txt']
                #Simple pdf rename case
                if len(subs) == 1 and subs[0][1] == 'pdf':
                    subprocess.run(['mv',
                                    '.'.join(subs[0]),
                                    '-'.join([assignment_name, ku_id, name]) + '.pdf'])
                #Convert multiple images into a single pdf
                elif subs[0][1] not in ['doc', 'docx']:
                    files = ['.'.join(sub) for sub in subs]
                    subprocess.run(['convert'] +
                                   files +
                                   ['-'.join([assignment_name, ku_id, name]) + '.pdf'])
                    subprocess.run(['rm'] + files)
                #Convert word to pdf using a headless libreoffice
                elif len(subs) == 1 and subs[0][1] in ['doc', 'docx']:
                    subprocess.run(['soffice', '--convert-to', 'pdf', '.'.join(subs[0])])
                    subprocess.run(['mv',
                                    subs[0][0]+'.pdf',
                                    '-'.join([assignment_name, ku_id, name]) + '.pdf'])
                    subprocess.run(['rm', '.'.join(subs[0])])
                else:
                    pass
            #Display results for double checking
            subprocess.run(['ls'])
                    
