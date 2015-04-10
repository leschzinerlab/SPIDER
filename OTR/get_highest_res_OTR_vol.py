#!/usr/bin/env python

import optparse
from sys import *
import os,sys,re
from optparse import OptionParser
import glob
import subprocess
from os import system
import linecache
import time
#=========================
def setupParserOptions():
        parser = optparse.OptionParser()
        parser.set_usage("%prog --folder=<OTR folder>")
        parser.add_option("--folder",dest="folder",type="string",metavar="FILE",
                help="OTR volume output folder")
        parser.add_option("-d", action="store_true",dest="debug",default=False,
                help="debug")
        options,args = parser.parse_args()

        if len(args) > 0:
                parser.error("Unknown commandline options: " +str(args))

        if len(sys.argv) < 2:
                parser.print_help()
                sys.exit()
        params={}
        for i in parser.option_list:
                if isinstance(i.dest,str):
                        params[i.dest] = getattr(options,i.dest)
        return params

#==============================
def checkConflicts(params):

	if not os.path.exists(params['folder']):
		print 'Folder %s does not exist. Exiting\n' %(params['folder'])
		sys.exit()

#=============================
def getNumberOfFolders(folder):

	counter=1
	max=20000
	currentMaxFolder=0

	while counter < max: 

		if os.path.exists('%s/selectFiles/sel%04d' %(folder,counter)):
			currentMaxFolder=counter	
		
		counter = counter + 1

	return currentMaxFolder

#==============================
def getHighestRes(resolution):

	highestRes=10000
	f1 = open(resolution,'r')

	for line in f1:

		if float(line.split()[1]) < highestRes:
			highestRes=float(line.split()[1])
			vol=(line.split()[0])
	
	return highestRes,vol

#==============================
if __name__ == "__main__":

	params=setupParserOptions()
	checkConflicts(params)

	#Get number of folders
	numFolders=getNumberOfFolders(params['folder'])
	
	if params['debug'] is True:
		print 'Number of folders = %s\n' %(str(numFolders))

	#Read highest resolution per OTR volume, record in a new file
	#----> If output file exists creat a new file
	if os.path.exists('%s/OTR_vol_resolutions.txt' %(params['folder'])):
		os.remove('%s/OTR_vol_resolutions.txt' %(params['folder']))

	if os.path.exists('%s/OTR_vol_resolutions_sorted.txt' %(params['folder'])):
		os.remove('%s/OTR_vol_resolutions_sorted.txt' %(params['folder']))

	o1 = open('%s/OTR_vol_resolutions.txt' %(params['folder']),'w')

	foldercounter=1

	while foldercounter <= numFolders:

		highestres,vol = getHighestRes('%s/selectFiles/sel%04d/resolution' %(params['folder'],foldercounter))

		o1.write('%s/selectFiles/sel%04d/%s\t%s\n' %(params['folder'],foldercounter,vol,str(round(highestres))[:-2]))
	
		foldercounter=foldercounter+1

	cmd = 'sort -k 2 -nr %s/OTR_vol_resolutions.txt' %(params['folder'])
	if params['debug'] is True:
		print cmd
	subprocess.Popen(cmd,shell=True).wait()	
