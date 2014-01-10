#!/usr/bin/env python

#This will copy files from leginon that have a matching defocal pair.  This script will
# loop through the [session].shifts.txt file found in the appion output for a given particle picking run.

#To run:

#  ./copy_focal_pairs_fromTXT.py [session].shifts.txt 

import glob
import re
import os
import sys

file=sys.argv[1]

input = open(file)

for line in input:
	
	tmp = line.rsplit()
	en = ("%s.mrc" %(tmp[0]))
	ef = ("%s.mrc" %(tmp[1]))
	
	enPath = ("/leginon2/michael/11mar22d/rawdata/%s" %(en))
	efPath = ("/leginon2/michael/11mar22d/rawdata/%s" %(ef))
	
	
	os.symlink(enPath,en)
	os.symlink(efPath,ef)