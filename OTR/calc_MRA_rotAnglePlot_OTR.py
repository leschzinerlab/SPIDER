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
	parser.add_option("--problimit",dest="problimit",type="float",metavar="FLOAT",default=0.001,
                help="Probability limit for assessing in-plane rotation angle distributions. (Default=0.001)")
	parser.add_option("--angularbin",dest="angularbin",type="int",metavar="INT",default=10,
                help="Angle bin size for calculating MRA rotation angle histogram (Default=10)")
        parser.add_option("--noMRAplot", action="store_true",dest="noMRAplot",default=False,
                help="Re-calculate probability distribution per class without re-calculating MRA ferris wheel plot")
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
def checkConflicts(params,outfile):

	if not os.path.exists(params['folder']):
		print 'Folder %s does not exist. Exiting\n' %(params['folder'])
		sys.exit()

	if os.path.exists(outfile):
        	print 'Output file %s already exists. Exiting.' %(outfile)
                sys.exit()

	if os.path.exists('%s_classAvgInfo.spi' %(outfile[:-4])):
		print 'Output file %s_classAvgInfo.spi already exists. Exiting.' %(outfile[:-4])
		sys.exit()

	if params['noMRAplot'] is False:
		if os.path.exists('%s/selectFiles/sel0001/mraPlot_perPartAngle0001.spi' %(params['folder'])):
			print 'Output file %s/selectFiles/sel0001/mraPlot_perPartAngle0001.spi already exists. Exiting.' %(params['folder'])
			sys.exit()
	
		if os.path.exists('%s/selectFiles/sel0001/mraPlot0001.spi' %(params['folder'])):
			print 'Output file %s/selectFiles/sel0001/mraPlot0001.spi already exists. Exiting' %(params['folder'])
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

#=============================
def calcMRAplot(params,numAvgs,outfile):

	spi='UD N [numParts]\n' 
	spi+='%s/rot_shifts\n' %(params['folder'])
	spi+='[one]=1\n'
	spi+='do lb11 [avg]=1,%s\n' %(str(numAvgs))
	spi+='UD N [numPartsClass]\n'
	spi+='%s/selectFiles/sel{****[avg]}\n' %(params['folder'])
	spi+='SD IC NEW\n'
	spi+='incore_angle2\n'
	spi+='1,([numPartsClass])\n'
	spi+='SD IC NEW\n'
	spi+='incore_angle\n'
	spi+='2,([numPartsClass]*2)\n'
	spi+='PT\n'
	spi+='%s/selectFiles/sel{****[avg]}/mraPlot{****[avg]}\n'%(params['folder'])
	spi+='128,128\n'
	spi+='P\n'
	spi+='1\n'
	spi+='64,64\n'
	spi+='N\n'
	spi+='do lb12 [particle]=1,[numPartsClass]\n'
	spi+='UD IC [particle] [select]\n'
	spi+='%s/selectFiles/sel{****[avg]}\n'%(params['folder'])
	spi+='UD IC [select] [angle]\n'
	spi+='%s/rot_shifts\n' %(params['folder'])
	spi+='IF([angle].LT.0) THEN\n'
	spi+='[angle]=360+[angle]\n'
	spi+='ENDIF\n'
	spi+='[x1]=(64+(64*COS([angle])))\n'
	spi+='[y1]=(64+(64*SIN([angle])))\n'
	spi+='[oppositeAngle]=[angle]+180\n'
	spi+='IF([oppositeAngle].GT.360)THEN\n'
	spi+='[oppositeAngle]=[oppositeAngle]-360\n'	
	spi+='ENDIF\n'	
	spi+='[x2]=(64+(64*COS([oppositeAngle])))\n'	
	spi+='[y2]=(64+(64*SIN([oppositeAngle])))\n'
	spi+='[first]=(2*[particle])-1\n'	
	spi+='[second]=[first]+1\n'
	spi+='SD IC [particle] [angle]\n'
	spi+='incore_angle2\n'
	spi+='SD IC [first] [x1] [y1]\n'	
	spi+='incore_angle\n'
	spi+='SD IC [second] [x2] [y2]\n'
	spi+='incore_angle\n'
	spi+='PT\n'
	spi+='%s/selectFiles/sel{****[avg]}/mraPlot{****[avg]}\n'%(params['folder'])
	spi+='L\n'
	spi+='[x1],[y1]\n'
	spi+='[x2],[y2]\n'
	spi+='N\n'
	spi+='lb12\n'
	spi+='SD IC COPY\n'
	spi+='incore_angle2\n'
	spi+='%s/selectFiles/sel{****[avg]}/mraPlot_perPartAngle{****[avg]}\n' %(params['folder'])
	spi+='SD IC COPY\n'
	spi+='incore_angle\n'
	spi+='%s/selectFiles/sel{****[avg]}/mraPlot_angles{****[avg]}\n' %(params['folder'])
	spi+='SD ICE\n'
	spi+='incore_angle\n'
	spi+='SD ICE\n'
	spi+='incore_angle2\n'
	spi+='UD ICE\n'
	spi+='%s/selectFiles/sel{****[avg]}\n'%(params['folder'])
	spi+='UD ICE\n'
	spi+='%s/rot_shifts\n' %(params['folder'])
	spi+='lb11\n'
	spi+='do lb21 [indiv]=1,%s\n' %(str(numAvgs))
	spi+='CP\n'
	spi+='%s/selectFiles/sel{****[indiv]}/mraPlot{****[indiv]}\n'%(params['folder']) 
	spi+='%s@{****[indiv]}\n' %(outfile[:-4])
	spi+='lb21\n'
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
def calc_prob(params,numFolders,outfile):

	#Create histogram bins:
	#currentAngle=0-float(params['angularbin'])/2	
	currentAngle=0
	bins=[]
	while currentAngle<360+float(params['angularbin']):
		bins.append(currentAngle)
		currentAngle=currentAngle+float(params['angularbin'])
	
	avg=1
	outinfo='%s_classAvgInfo.spi' %(outfile[:-4])
	
	#Creat output file
	mra_out=open(outinfo,'a')

	#Loop over all classes
	while avg <= numFolders:

		#Create array of all inplane MRA angles for this class
		if not os.path.exists('%s/selectFiles/sel%04i/mraPlot_perPartAngle%04i.spi' %(params['folder'],avg,avg)):
			print 'Cannot find file %s/selectFiles/sel%04i/mraPlot_perPartAngle%04i.spi.' %(params['folder'],avg,avg)

		angles=np.genfromtxt('%s/selectFiles/sel%04i/mraPlot_perPartAngle%04i.spi' %(params['folder'],avg,avg),usecols = (2))
		
		if params['debug'] is True:
			print angles

		#Calculate histogram
		n, bins_out, patches = P.hist(angles, bins, histtype='stepfilled')

		if params['debug'] is True:
			print 'Histogram'
			print n

		#Equation setup
		numberOfParticles=len(angles)
		numberOfAngularBins=len(n)
		if params['debug'] is True:
			print 'Number of particles=%i' %(numberOfParticles)
			print 'Number of angular bins=%i' %(numberOfAngularBins)
		
		q=float(float(params['angularbin'])/360.0)
		N=float(numberOfParticles)

		#Calc probability per class average
		counter=0
		numberGoodBins=0
		while counter<numberOfAngularBins:
	
			X=float(n[counter])
			probability=float(calc_prob_binomial(X,q,N))
			if probability <params['problimit']:	
				if params['debug'] is True:
					print 'Working on bin %i+/-%i degress. Number of particles = %i; P=%.4f < -------> Outside of probability limit' %(counter*params['angularbin'],params['angularbin'],n[counter],probability)
			if probability >params['problimit']:
				numberGoodBins=numberGoodBins+1	
				if params['debug'] is True:
					print 'Working on bin %i+/-%i degress. Number of particles = %i; P=%.4f' %(counter*params['angularbin'],params['angularbin'],n[counter],probability)
		
			counter=counter+1
		
		if params['debug'] is True:
			print 'For class %i; %i/%i good bins (P>%f)' %(avg,numberGoodBins,numberOfAngularBins,params['problimit'])

		#Write out to text file:
		mra_out.write('%i\t3\t%.3f\t%i\t%i\n' %(avg,float(numberGoodBins)/float(numberOfAngularBins),numberGoodBins,numberOfAngularBins))

		avg=avg+1

	mra_out.close()
#================================
def calc_prob_binomial(X,q,N):

	'''
	Binomial probability distribution: 

	                 N!           X        N-X
		P = -------------- * q  * (1-q)
    		      X! (N-X)!
	
	
		  |---------------||--------------|
		    First half         second half
	
	P: The probability of finding the X particles in the range [L,M] given N particles in the class
	N: number of particles in class
	X: number of particles in the angular range 
	q: probability of finding one particle in that range

            AngularRange
	q = ------------
	       360
	'''
	
	firstHalf=(math.factorial(N))/((math.factorial(X))*(math.factorial(N-X)))	
	secondHalf=(math.pow(q,X))*(math.pow((1-q),(N-X)))
	probability=firstHalf*secondHalf

	return probability

#==============================
def add_label(params,numFolders,outfile):

	spi='[tot]=%i\n' %(numFolders)
	spi+='do lb1 [avg]=1,[tot]\n' 
	spi+='UD IC [avg] [bl] [good] [tot]\n' 
	spi+='%s_classAvgInfo\n' %(outfile[:-4])
	spi+='LA\n'
	spi+='%s@{******[avg]}\n' %(outfile[:-4])
	spi+='%s_w_label@{*******[avg]}\n' %(outfile[:-4])
	spi+='{***[good]}/{***[tot]}\n'
	spi+='lb1\n'	
	spi+='UD ICE\n'
	spi+='%s_classAvgInfo\n' %(outfile[:-4])
	runSpider(spi)

#==============================
if __name__ == "__main__":

	params=setupParserOptions()
	prob=str(params['problimit']).split('.')[1]
	outfile='%s/MRA_OTR_angles_p%s_AngBin%02i.spi' %(params['folder'],prob,params['angularbin'])
	
	if params['debug'] is True:
		print outfile
	
	checkConflicts(params,outfile)

	#Get number of folders
	numFolders=getNumberOfFolders(params['folder'])
	
	if params['debug'] is True:
		print 'Number of folders = %s\n' %(str(numFolders))

	if params['noMRAplot'] is False:
		calcMRAplot(params,numFolders,outfile)
		
	calc_prob(params,numFolders,outfile)
	add_label(params,numFolders,outfile)
	
	#Flip handedness of labeled stack
	cmd='proc2d %s_w_label.spi %s_w_label.spi flip inplace'%(outfile[:-4],outfile[:-4])
	if params['debug'] is True:
		print cmd
	subprocess.Popen(cmd,shell=True).wait()	
	
	if params['debug'] is False:
		os.remove(outfile)
