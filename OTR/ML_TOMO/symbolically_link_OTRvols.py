#!/usr/bin/env python

import os
import sys

##############
##############
#Inputs:

####OTR output directory
OTRdir='/labdata/allab/indrajit/SRW1_TER_OTR/MSA-MRA/OTR_all_ali13/'

####Volume number from centering routine that will be used for classification
volumeNumberFromCentering=6

####Output folder
newdir='vols'

##############
##############
if os.path.exists(newdir):
	print 'Output directory %s already exists. Exiting.' %(newdir)
	sys.exit()

#Get number of volumes
counter=1
maxlimit=5000
volcounter=0
while counter < maxlimit:

	if os.path.exists('%s/selectFiles/sel%04d/vol%03d.spi' %(OTRdir,counter,volumeNumberFromCentering)):
		volcounter=volcounter+1
	counter=counter+1

print 'Number of volumes = %.f' %(volcounter)

if volcounter == 0:
	print 'Error: No volumes found. Exiting' 
	sys.exit()

#Symbolically link volumes to new folder

os.makedirs(newdir)

counter=1

while counter <= volcounter:
	os.symlink('%s/selectFiles/sel%04d/vol%03d.spi' %(OTRdir,counter,volumeNumberFromCentering),'%s/sel%04d_vol%03d.spi' %(newdir,counter,volumeNumberFromCentering))
	counter = counter + 1
