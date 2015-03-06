#!/usr/bin/env python2.4

import tarfile
import random
import shutil
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
        parser.set_usage("%prog --micros=<wild card for untilted micrographs> --scripts=<path>")
        parser.add_option("--micros",dest="micros",type="string",metavar="FILE",
                help="Untilted micrographs (e.g 'tmp/*.mrc'); assumes that .box files have the same name except with .box and that tilted micrographs have the same name except with a different extension (00 or 01). Output files are put into your current working directory")
	parser.add_option("--scripts",dest="scripts",type="string",metavar="STRING",
                help="Path to spider scripts directory")
	parser.add_option("-d", action="store_true",dest="debug",default=False,
                help="debug")
        options,args = parser.parse_args()

        if len(args) > 1:
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
def getEMANPath():
        emanpath = subprocess.Popen("env | grep EMAN2DIR", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
        if emanpath:
                emanpath = emanpath.replace("EMAN2DIR=","")
        if os.path.exists(emanpath):
                return emanpath
        print "EMAN2 was not found, make sure eman2 is in your path"
        sys.exit()

#=============================
def box_to_spi(boxfile,spiout):

        f1 = open(boxfile,'r')

        o1 = open(spiout,'w')

        count = 1

        for line in f1:
                l = line.split()

                x = float(l[0])
                y = float(l[1])
                box = float(l[2])/2

                o1.write('%i\t4\t%i\t%f\t%f\t1\n' %(count,count,x+box,y+box))
                count = count + 1

	return l[2]

#==============================
def spi_to_box(spifile1,boxsize,outbox1,spifile2,outbox2):
        
	o1 = open(outbox1,'w')
	o2 = open(outbox2,'w')
        tot = len(open(spifile1,'r').readlines())
	i = 1
	boxsize=float(boxsize)

        while i <= tot:

		l1 = linecache.getline(spifile1,i)
		l2 = linecache.getline(spifile2,i)

		line1 = l1.split()
		line2 = l2.split()

		if len(l1) == 0:
			i = i + 1
			continue

		print l1
		print len(l1)
		print l1[1]
	
                if l1[1] == ";":
                        print l1[1]
			i = i + 1
			continue

                x1 = float(line1[3])-boxsize/2
                y1 = float(line1[4])-boxsize/2
		x2 = float(line2[3])-boxsize/2
                y2 = float(line2[4])-boxsize/2

		if x1+boxsize+2 < 4096: 
			if y1+boxsize+2 < 4096:
				if x2+boxsize+2 < 4096:
					if y2+boxsize+2 < 4096:
                				o1.write('%i\t%i\t%i\t%i\t-3\n' %(int(x1),int(y1),int(boxsize),int(boxsize)))
						o2.write('%i\t%i\t%i\t%i\t-3\n' %(int(x2),int(y2),int(boxsize),int(boxsize)))

		i = i + 1

	o1.close()
	o2.close()

#==============================
if __name__ == "__main__":

	#Get inputs from command line
        params=setupParserOptions()

	#Check that eman2 is loaded
	getEMANPath()

	#Set paths
	pathtoscripts = params['scripts']

	#Create list of untilted micrographs
	microlist = glob.glob(params['micros'])

	if params['debug'] is True:
		print microlist

	#Copy spider scripts to your output directorysubprocess.Popen(cmd,shell=True).wait()
	cmd = 'cp %s/*.spi .' %(pathtoscripts)
	subprocess.Popen(cmd,shell=True).wait()

	cmd = 'cp %s/boxer_to_spi.py .' %(pathtoscripts)
        subprocess.Popen(cmd,shell=True).wait()

	i = 1
	
	for untiltedmicro in microlist: 

		if params['debug'] is True:
			print 'Untilted micro = %s' %(untiltedmicro)
	
		ext = untiltedmicro[-6:][:-4]

		#Create .box file name by removing extension
		untiltedbox = '%s.box' %(untiltedmicro[:-4])
		untiltedbox_out = '%s_align.box' %(untiltedmicro[:-4])

		if params['debug'] is True:
			print 'Untilted box = %s' %(untiltedbox)

		if not os.path.exists(untiltedbox):
			continue

		if os.path.getsize(untiltedbox) == 0:
			print 'No particles in %s. Skipping.' %(untiltedbox) 
			continue

		#Check to see that untilted box file doesn't exist
		if os.path.exists(untiltedbox_out):
			print 'Error: Box file %s exists. Skipping micrograph %s' %(untiltedbox_out,untiltedmicro)
			continue

		#Create tilted micro & box name by removing '01.mrc' and replacing with '00.mrc' or '00.box'
		if ext == '00':
			tiltmicro = untiltedmicro.replace('00.mrc','01.mrc')
			tiltbox = untiltedmicro.replace('00.mrc','01_align.box')

		if ext == '01': 
			tiltmicro = untiltedmicro.replace('01.mrc','00.mrc')
			tiltbox = untiltedmicro.replace('01.mrc','00_align.box')

		if os.path.exists(tiltbox):
                        print 'Error: Box file %s exists. Skipping micrograph %s' %(tiltbox,tiltmicro)
                        continue
	
		if params['debug'] is True:
			print 'Tilted micro = %s' %(tiltmicro)

		if not os.path.exists(tiltmicro):
			print 'Tilted micro %s doesnt exist, skipping' %(tiltmicro)
			continue

		#Create .spi files from .mrc inputs and normalize
		cmd = 'e2proc2d.py %s image_00286_01.spi --outtype spidersingle --process normalize' %(tiltmicro)
		if params['debug'] is True:
			print cmd
		subprocess.Popen(cmd,shell=True).wait()
	
		cmd = 'e2proc2d.py %s image_00286_00.spi --outtype spidersingle --process normalize' %(untiltedmicro)
		if params['debug'] is True:
			print cmd
		subprocess.Popen(cmd,shell=True).wait()

		#Convert input box files into spider format - (input box file,output spider file name)
		boxsize = box_to_spi(untiltedbox,'coordinates_micrograph_286.spi')
		
		#Create spider output directory
		cmd = 'mkdir output'
		subprocess.Popen(cmd,shell=True).wait()

		#Run spider command
		cmd = 'spider spi @b00.find_tlt_parts_final'
		subprocess.Popen(cmd,shell=True).wait()

		#Convert spi files into box format
		#spi_to_box('output/final_tlt_coordinates_00286.spi',boxsize,tiltbox,'output/final_unt_coordinates_00286.spi',untiltedbox_out)

		cmd = './boxer_to_spi.py %s' %(str(boxsize))
		subprocess.Popen(cmd,shell=True).wait()

		shutil.move('output/final_tlt_coordinates_00286_out.box',tiltbox)
		shutil.move('output/final_unt_coordinates_00286_out.box',untiltedbox_out) 

		#Copy apsh file
		cmd = 'cp output/apsh_00286.spi %s_apsh.spi' %(untiltedbox_out[:-4])
		subprocess.Popen(cmd,shell=True).wait()

		#Clean up
		cmd = 'rm -r output _10.spi coordinates_micrograph_286.spi dummy_angles.spi image_00286_00.spi image_00286_01.spi' 
		subprocess.Popen(cmd,shell=True).wait()

		i = i + 1
	
	#Final clean up
	cmd = 'rm boxer_to_spi.py p.* b00.find_tlt_parts_final.spi'
	subprocess.Popen(cmd,shell=True).wait()
	
