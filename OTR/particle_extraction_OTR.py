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
        parser.set_usage("%prog -u <untiltCTF> -t <tiltCTF> --binning=<binning factor> --output=<stack.img>")
        parser.add_option("-u",dest="untiltCTF",type="string",metavar="FILE",
                help="CTFTILT output file for untilted micrographs")
	parser.add_option("-t",dest="tiltCTF",type="string",metavar="FILE",
                help="CTFTILT output file for tilted micrographs")
        parser.add_option("--binning",dest="binning",type="int", metavar="INT",default=2,
                help="Binning factor for final particle stack. (Default = 2)")
	parser.add_option("--output",dest="output",type="string", metavar="STRING",
                help="Output basename for tilted and untilted stacks (no extension)")
        parser.add_option("-d", action="store_true",dest="debug",default=False,
                help="debug")
        options,args = parser.parse_args()

        if len(args) > 0:
                parser.error("Unknown commandline options: " +str(args))

        if len(sys.argv) < 3:
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
        print "EMAN2 was not found, make sure eman2 is loaded"
        sys.exit()

#=============================
def checkConflicts(params):
        if not params['untiltCTF']:
                print "\nWarning: no untilted CTFTILT input specified\n"
		sys.exit()
	if not params['tiltCTF']:
                print "\nWarning: no tilted CTFTILT input specified\n"
		sys.exit()
	if os.path.exists('%s_tilt.img' %(params['output'])):
		print "\nError: Output stack %s_tilt.img already exists. Exiting." %(params['output'])
		sys.exit()	
	if os.path.exists('%s_untilt.img' %(params['output'])):
		print "\nError: Output stack %s_untilt.img already exists. Exiting." %(params['output'])
		sys.exit()
	if os.path.exists('%s_tilt_info.txt' %(params['output'])):
		print "\nError: Output file %s_tilt_info.txt already exists. Exiting." %(params['output'])
		sys.exit()	
	if os.path.exists('%s_untilt_info.txt' %(params['output'])):
		print "\nError: Output file %s_untilt_info.txt already exists. Exiting." %(params['output'])
		sys.exit()

#=============================
def getNumberOfLines(f1):
	
	totallines=len(open(f1,'r').readlines())
	return totallines

#=============================
def getMicroCTFinfo(ctftilt,linenumber):
	
	l1 = linecache.getline(ctftilt,linenumber)
	micro = l1.split()[0]

	return micro,l1

#==============================
def getTiltedMicroCTFinfo(ctftilt,untiltmicro):

	f1 = open(ctftilt,'r')

	for line in f1:
		l = line.split()
		if l[0][:-6] == untiltmicro[:-6]:
			return l[0],line

	return 'blank','blank'

#=============================
def writeCTFinfo(ctf,numlines,output):

	counter=1
	while counter<=numlines:
		output.write(ctf)
		counter = counter + 1

#=============================
def extract_particles(micro,output,boxfile,binning,debug):

	#Extract particles 
	cmd = 'batchboxer input=%s dbbox=%s output=tmp.img' %(micro,boxfile)
	if debug is True:
		print cmd
	subprocess.Popen(cmd,shell=True).wait()

	#Bin stack
	cmd = 'e2proc2d.py tmp.img %s --meanshrink %i' %(output,binning)
	if debug is True:
		print cmd
	subprocess.Popen(cmd,shell=True).wait()

	os.remove('tmp.img')
	os.remove('tmp.hed')

#=============================
def startLoopOverMicros(params,boxextension):

	#Get total number of tilt mates
	numLines = getNumberOfLines(params['untiltCTF']) 

	if params['debug'] is True:
		print 'Number of lines in untilted ctftilt file = %i' %(numLines-1)

	#Starting at line 2 b/c the first line has parameters in it	
	counter=2

	untiltOutput=open('%s_untilt_info.txt' %(params['output']),'a')    #'a' is append. It's like 'w' but easier for large loops
	tiltOutput=open('%s_tilt_info.txt' %(params['output']),'a')

	#loop over all micrographs
	while counter <= numLines:
		
		#Get untilt micro name & ctf info
		untiltmicro,untiltCTFinfo = getMicroCTFinfo(params['untiltCTF'],counter)
		
		#Get tilted micro info
		tiltmicro,tiltCTFinfo = getTiltedMicroCTFinfo(params['tiltCTF'],untiltmicro)

		if tiltmicro is 'blank':
			print 'Untilted micro %s does not have a tilt mate' %(untiltmicro)
			counter = counter + 1
			continue

		if params['debug'] is True:
			print 'Tilted micro %s CTFTILT info: %s' %(tiltmicro,tiltCTFinfo)
			print 'Untilted micro %s CTFTILT info: %s' %(untiltmicro,untiltCTFinfo)

		#Create box file names
		tiltbox='%s%s' %(tiltmicro[:-4],boxextension)
		untiltbox='%s%s' %(untiltmicro[:-4],boxextension)
		
		#Check that tilted box file exists
		if not os.path.exists(tiltbox):
			print 'Tilted micro %s does not have a box file' %(tiltmicro)
			counter = counter + 1
			continue

		if params['debug'] is True:
			print 'Tilted box file for %s is %s' %(tiltmicro,tiltbox)
			print 'Untilted box file for %s is %s' %(untiltmicro,untiltbox)

		#Check that they have the same number of entries
		if not getNumberOfLines(tiltbox) == getNumberOfLines(untiltbox):
			print '%s  <---> %s  do not have the same number of particles' %(tiltbox,untiltbox)
			counter = counter + 1
			continue

		#Write CTF info to output text files
		if params['debug'] is True:
			print "Writing %i lines of CTF info: %s for tilted" %(getNumberOfLines(tiltbox),tiltCTFinfo)
			print "Writing %i lines of CTF info: %s for untilted" %(getNumberOfLines(untiltbox),untiltCTFinfo)

		writeCTFinfo(untiltCTFinfo,getNumberOfLines(untiltbox),untiltOutput)
		writeCTFinfo(tiltCTFinfo,getNumberOfLines(tiltbox),tiltOutput)

		extract_particles(tiltmicro,'%s_tilt.img' %(params['output']),tiltbox,params['binning'],params['debug'])
		extract_particles(untiltmicro,'%s_untilt.img' %(params['output']),untiltbox,params['binning'],params['debug'])

		counter = counter + 1

#==============================
if __name__ == "__main__":

	boxextension = '_align.box'

	getEMANPath()
	params=setupParserOptions()
	checkConflicts(params)
	print 'made it here'
	#Starts here
	startLoopOverMicros(params,boxextension)

	


		
