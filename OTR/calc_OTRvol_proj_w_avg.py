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
import numpy as np
import pylab as P
import matplotlib
import math

#=========================
def setupParserOptions():
        parser = optparse.OptionParser()
        parser.set_usage("%prog --folder=<OTR folder>")
        parser.add_option("--folder",dest="folder",type="string",metavar="FILE",
                help="OTR volume output folder")
        parser.add_option("--avgs",dest="avgs",type="string",metavar="FILE",
                help="2D class average stack (.img) from which the OTR volumes were calculated")
	parser.add_option("--box",dest="box",type="int",metavar="INT",
                help="Box size (Needs to be the same b/w the class averages & volumes)")
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
def checkConflicts(params):

	if not params['box']:
		print '\nError: No box size specified. Exiting\n' 
		sys.exit()

	if not params['folder']:
		print '\nError: OTR folder not specified. Exiting.\n'
		sys.exit()
	if not os.path.exists(params['folder']):
		print '\nError: OTR folder %s does not exist. Exiting.\n' %(params['folder'])
		sys.exit()

	if not os.path.exists(params['avgs']):
		print '\nError: Class averages stack %s does not exist. Exiting.\n' %(params['avgs'])
		sys.exit()

	if params['avgs'][-4:] != '.img': 
		if params['avgs'][-4:] != '.hed':
			print '\nError: Class average extension %s not recognized as .img or .hed. Exiting\n' %(params['avgs'][-4:])
			sys.exit()

#==============================
def alignVols(params,numFolders):

	outfile='%s/%s_alignedOTRproj.spi' %(params['folder'],params['avgs'][:-4])

	if os.path.exists(outfile):
		os.remove(outfile)

	#Since we projecting along the Z axis: phi = psi = theta = 0
	angleout='%s/%s_euler.spi' %(params['folder'],params['avgs'][:-4])
	if params['debug'] is True:
		print angleout
	if os.path.exists(angleout):
		os.remove(angleout)
	angleoutappend=open(angleout,'a')
	angleoutappend.write('1\t3\t0\t90\t0\n')
	angleoutappend.close()
	
	#selectFiles/sel0001/vol006_fq.spi

	spi='[counter]=1\n' 
	spi+='do lb1 [avg]=1,%i\n' %(int(numFolders))
	spi+='[next]=[counter]+1\n'
	spi+='[this]=[counter]+2\n'
	spi+='CP\n'
	spi+='%s/%s_avgs@{*******[avg]}\n' %(params['folder'],params['avgs'][:-4])
	spi+='%s@{******[counter]}\n' %(outfile[:-4])
	spi+='PJ 3Q\n'
        spi+='%s/selectFiles/sel{****[avg]}/vol001_fq\n' %(params['folder'])
        spi+='%s\n' %(str(params['box']/2))
        spi+='1\n'
        spi+='%s\n' %(angleout[:-4])
        spi+='_1\n'
	spi+='CP\n'
        spi+='_1\n'
        spi+='%s@{******[next]}\n' %(outfile[:-4])
	spi+='DE\n'	
	spi+='_1\n'
	spi+='PJ 3Q\n' 
	spi+='%s/selectFiles/sel{****[avg]}/vol006_fq\n' %(params['folder'])
	spi+='%s\n' %(str(params['box']/2)) 
	spi+='1\n'
	spi+='%s\n' %(angleout[:-4])
	spi+='_1\n'
	spi+='CP\n'
        spi+='_1\n'
        spi+='%s@{******[this]}\n' %(outfile[:-4])
	spi+='[counter]=[counter]+3\n'
	spi+='DE\n'	
	spi+='_1\n'
	spi+='DE\n'	
	spi+='_2\n'
	spi+='lb1\n'
	runSpider(spi)

#===========================
def runSpider(lines):
       spifile = "currentSpiderScript.spi"
       if os.path.isfile(spifile):
               os.remove(spifile)
       spi=open(spifile,'w')
       spi.write("MD\n")
       spi.write("TR OFF\n")
       spi.write("MD\n")
       spi.write("VB OFF\n")
       spi.write("MD\n")
       spi.write("SET MP\n")
       spi.write("(8)\n")
       spi.write("\n")
       spi.write(lines)

       spi.write("\nEN D\n")
       spi.close()
       spicmd = "spider spi @currentSpiderScript"
       spiout = subprocess.Popen(spicmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stderr.read()
       output = spiout.strip().split()
       if "ERROR" in output:
               print "Spider Error, check 'currentSpiderScript.spi'\n"
               sys.exit()
       # clean up
       os.remove(spifile)
       if os.path.isfile("LOG.spi"):
               os.remove("LOG.spi")
       resultf = glob.glob("results.spi.*")
       if resultf:
               for f in resultf:
                       os.remove(f)

#==============================
if __name__ == "__main__":

        params=setupParserOptions()
        checkConflicts(params)

        #Get number of folders
        numFolders=getNumberOfFolders(params['folder'])

	#Convert stack to spider format
	cmd='proc2d %s %s/%s_avgs.spi spiderswap' %(params['avgs'],params['folder'],params['avgs'][:-4])
	if params['debug'] is True: 
		print cmd
	if os.path.exists('%s/%s_avgs.spi' %(params['folder'],params['avgs'][:-4])):
		os.remove('%s/%s_avgs.spi' %(params['folder'],params['avgs'][:-4]))
	subprocess.Popen(cmd,shell=True).wait()

	alignVols(params,numFolders)	
