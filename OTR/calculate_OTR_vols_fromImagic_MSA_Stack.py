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
        parser.set_usage("%prog --stack=<mergedImagicStack> --orig=<origStack> --info=<mergedInfoFile> --output=<folder> --angle=<angle> --apix=<apix> --lp=<lp> --radius=<rad>")
        parser.add_option("--stack",dest="stack",type="string",metavar="FILE",
                help="Aligned merged stack with combined +/- tilts from MSA-MRA")
	parser.add_option("--orig",dest="orig",type="string",metavar="FILE",
                help="Original merged imagic stack")
	parser.add_option("--info",dest="info",type="string",metavar="FILE",
                help="Corresponding merged tilt-info file for each particle")
	parser.add_option("--output",dest="folder",type="string", metavar="STRING",
                help="Output folder")
	parser.add_option("--angle",dest="angle",type="int", metavar="INT",
                help="Approximate tilt angle for 'untilted' particles (first half of the merged stack) (e.g. 45)")
	parser.add_option("--apix",dest="apix",type="float", metavar="FLOAT",
                help="Pixel size")
	parser.add_option("--lp",dest="lp",type="int", metavar="INT",
                help="Low pass filter for OTR volumes during particle centering alignment")
	parser.add_option("--radius",dest="radius",type="int", metavar="INT",
                help="Radius (pixels) for 3D reconstruction")
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

#=============================
def checkConflicts(params):
        if os.path.exists(params['folder']):
                print "\nError: Output folder %s already exists. Exiting." %(params['folder'])
                sys.exit()
	if not os.path.exists(params['stack']):
		print "\nError: Input stack %s does not exist. Exiting." %(params['stack'])
		sys.exit()
	if not os.path.exists(params['info']):
                print "\nError: Input file %s does not exist. Exiting." %(params['info'])
                sys.exit()
	if getNumberOfLines(params['info'])%2 == 1:
		print "\nError: Input file %s has an odd number of lines - should be even. Exiting." %(params['info'])
		sys.exit()

#=============================
def getNumberOfLines(f1):

        totallines=len(open(f1,'r').readlines())
        return totallines

#==============================
def getRotShifts(input,output,imagicdir,debug):

	#Write imagic batch: TEMPLATE

	#!/bin/csh -f
	#setenv IMAGIC_BATCH 1
	#echo "!  "
	#echo "! -------------------- IMAGIC ACCUMULATE FILE-------------------- "
	#echo "! "
	#echo "! IMAGIC-PROGRAM : stand:headers.e "
	#echo "! "
	#/programs/i386-linux/imagic/leschziner/stand/headers.e <<EOF
	#all_ali7
	#PLT_OUT
	#SHIFT
	#all_ali7.plt
	#EOF
	
	cmd='#!/bin/csh -f\n'
	cmd+='setenv IMAGIC_BATCH 1\n'
	cmd+='%s/stand/headers.e <<EOF\n' %(imagicdir)	
	cmd+='%s\n' %(input[:-4])
	cmd+='PLT_OUT\n' 
	cmd+='SHIFT\n' 
	cmd+='%s\n' %(output)
	cmd+='EOF\n'	
	cmd+='touch header_done\n'

	runCMD(cmd,debug,'header_done')

#===============================
def runCMD(cmd,debug,touch_out):

	if debug is True:
                print cmd

	if os.path.exists('tmp.csh'):
		os.remove('tmp.csh')
        tmp = open('tmp.csh','w')
        tmp.write(cmd)
        tmp.close()

        cmd = 'chmod +x tmp.csh'
        subprocess.Popen(cmd,shell=True).wait()

        cmd = './tmp.csh'
        subprocess.Popen(cmd,shell=True).wait()

        wait(touch_out,debug)
	
	os.remove('tmp.csh')

#==============================
def wait(testFile,debug):

        testExists = False

        while testExists is False:

                test = os.path.isfile(testFile)

                if test is False:
                        if debug is True:
				print '%s does not exist yet' %(testFile)
                        testExists = False

                if test is True:
			if debug is True:
	                        print '%s exists' %(testFile)
                        testExists = True

#==============================
def getMembershipPerClass(input,output,imagicdir,debug):

	#!/bin/csh -f
	#setenv IMAGIC_BATCH 1
	#echo "!  "
	#echo "! -------------------- IMAGIC ACCUMULATE FILE-------------------- "
	#echo "! "
	#echo "! IMAGIC-PROGRAM : stand:headers.e "
	#echo "! "
	#/programs/i386-linux/imagic/leschziner/stand/headers.e <<EOF
	#all_ali7
	#PLT_OUT
	#MSA
	#msa
	#EOF

	cmd='#!/bin/csh -f\n'
        cmd+='setenv IMAGIC_BATCH 1\n'
        cmd+='%s/stand/headers.e <<EOF\n' %(imagicdir)
        cmd+='%s\n' %(input[:-4])
        cmd+='PLT_OUT\n'
        cmd+='MSA\n'
        cmd+='%s\n' %(output)
        cmd+='EOF\n'
        cmd+='touch header_done\n'

        runCMD(cmd,debug,'header_done')

#==============================
def createSpiderSelectFilesFromMembershipFile(input,folder,debug):

	os.mkdir('%s/selectFiles' %(folder))

	inputRead=open(input,'r')

	counter = 1

	numClasses=1

	for line in inputRead:

		classNumber = float(line.split()[0])

		if classNumber>numClasses:
			numClasses=classNumber
	
		if os.path.exists('%s/selectFiles/sel%04d.spi' %(folder,classNumber)):

			numLines=getNumberOfLines('%s/selectFiles/sel%04d.spi' %(folder,classNumber))

			out=open('%s/selectFiles/sel%04d.spi' %(folder,classNumber),'a')
			out.write('%i\t1\t%i\n' %(numLines+1,counter))

		if not os.path.exists('%s/selectFiles/sel%04d.spi' %(folder,classNumber)):

			out=open('%s/selectFiles/sel%04d.spi' %(folder,classNumber),'w')
                        out.write('1\t1\t%i\n' %(counter))	
			
		out.close()
		counter = counter + 1

	return numClasses

#==============================
def getEMANPath():
        emanpath = subprocess.Popen("env | grep EMAN2DIR", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
        if emanpath:
                emanpath = emanpath.replace("EMAN2DIR=","")
        if os.path.exists(emanpath):
                return emanpath
        print "EMAN2 was not found, make sure the EMAN2 module is loaded"
        sys.exit()

#==============================
def getIMAGICPath():
        emanpath = subprocess.Popen("env | grep IMAGIC", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
        if emanpath:
                emanpath = emanpath.replace("IMAGIC_ROOT=","")
        if os.path.exists(emanpath):
                return emanpath
        print "Imagic was not found, make sure the Imagic module is loaded"
        sys.exit()

#=============================
def writeSpiderEulerAngles(rotshifts,info,out,angle):

	if getNumberOfLines(rotshifts) != getNumberOfLines(info):
		print '%s has a different number of lines than %s. Exiting.' %(rotshifts,info)
		sys.exit()

	totPerTilt=getNumberOfLines(rotshifts)/2

	#Write euler angles for untilt -> tilt	
	o1=open(out,'w')
	line=1
	while line<= totPerTilt:

		rotline=linecache.getline(rotshifts,line)
		infoline=linecache.getline(info,line)
		infolineTilt=linecache.getline(info,line+totPerTilt)

		imagicAng=float(rotline.split()[1])
		imagicSX=float(rotline.split()[2])
		imagicSY=float(rotline.split()[3])

		ctftiltRotUntilt=float(infoline.split()[4])
		ctftiltAngUntilt=float(infoline.split()[5])	
		ctftiltRotTilt=float(infolineTilt.split()[4])
                ctftiltAngTilt=float(infolineTilt.split()[5])

		#Calc euler angles
		PHI= ctftiltRotTilt - 90 - imagicAng
		if PHI < 0:
			PHI = PHI+360
		THETA = ctftiltAngTilt - ctftiltAngUntilt  
		PSI = 90 - ctftiltRotUntilt 
		o1.write('%i\t3\t%s\t%s\t%s\n' %(line,str(PSI),str(THETA),str(PHI)))
		
		line = line + 1
	o1.close()

	#Write euler angles for tilt -> untilt  
        o1=open(out,'a')
        line=totPerTilt+1
        while line<= totPerTilt*2:

                rotline=linecache.getline(rotshifts,line)
                infoline=linecache.getline(info,line)
                infolineTilt=linecache.getline(info,line-totPerTilt)

                imagicAng=float(rotline.split()[1])
                imagicSX=float(rotline.split()[2])
                imagicSY=float(rotline.split()[3])

                ctftiltRotUntilt=float(infoline.split()[4])
                ctftiltAngUntilt=float(infoline.split()[5])
                ctftiltRotTilt=float(infolineTilt.split()[4])
                ctftiltAngTilt=float(infolineTilt.split()[5])

		PHI= ctftiltRotTilt - 90 - imagicAng
                if PHI < 0:
                        PHI = PHI+360
                THETA = ctftiltAngTilt - ctftiltAngUntilt
                PSI = 90 - ctftiltRotUntilt
                o1.write('%i\t3\t%s\t%s\t%s\n' %(line,str(PSI),str(THETA),str(PHI)))

                line = line + 1

#=============================
def recontruct_volume_and_refine(eulers,stack,numClasses,workingdir,debug,lp,apix,radius,rotShift):

	#Loop over all classes
	counter=1

	while counter<=numClasses:

		reconstruct(stack,'%s/selectFiles/sel%04d.spi' %(workingdir,counter),eulers,apix,lp)
		
		volcounter=1
                itermax=5

                while volcounter<=itermax:
			if volcounter==1:
				refine3D('%s/selectFiles/sel%04d' %(workingdir,counter),eulers,'%s/selectFiles/sel%04d/vol%03d' %(workingdir,counter,volcounter),'%s/selectFiles/sel%04d/vol%03d' %(workingdir,counter,volcounter+1),radius,rotShift,stack,apix,lp)
			if volcounter>1:
				refine3D('%s/selectFiles/sel%04d' %(workingdir,counter),eulers,'%s/selectFiles/sel%04d/vol%03d' %(workingdir,counter,volcounter),'%s/selectFiles/sel%04d/vol%03d' %(workingdir,counter,volcounter+1),radius,'blank',stack,apix,lp)
			volcounter=volcounter+1
		counter = counter +1

#==============================
def refine3D(workingdir,eulers,inputvol,outputvol,radius,rotShift,stack,apix,lp):

	numParts=getNumberOfLines('%s.spi'% (workingdir))

	lp1=(apix/lp)-0.025
	lp2=(apix/lp)+0.025

	spi='PJ 3Q\n'
	spi+='%s_filt%03dA\n' %(inputvol,lp)
	spi+='%s\n' %(str(radius))
	spi+='%s\n' %(workingdir)
	spi+='%s\n' %(eulers[:-4])
	spi+='%s_filt%03dA_proj@******\n' %(inputvol,lp)
	spi+='do lb1 [part]=1,%s\n' %(str(numParts))
	spi+='UD IC [part] [sel]\n' 
	spi+='%s\n' %(workingdir)
	if rotShift != 'blank':
		spi+='UD IC [sel] [rot] [sx] [sy]\n' 
		spi+='%s\n' %(rotShift)
		spi+='SH\n'
		spi+='%s@{*******[sel]}\n' %(stack[:-4])
		spi+='_5\n'
		spi+='-[sx],-[sy]\n'
	if rotShift == 'blank':
		spi+='CP\n'
		spi+='%s_parts_shifted@{*******[sel]}\n' %(inputvol)
		spi+='_5\n'
	spi+='CC N\n'
	spi+='_5\n'
	spi+='%s_filt%03dA_proj@{******[sel]}\n' %(inputvol,lp)
	spi+='_3\n'
	spi+='PK [xi] [yi]\n'
	spi+='_3\n'
	spi+='(1,0)\n'
	if rotShift != 'blank':
		spi+='[newx]=[sx]+[xi]\n' 
		spi+='[newy]=[sy]+[yi]\n'
	if rotShift == 'blank':
		spi+='[newx]=[xi]\n'
		spi+='[newy]=[yi]\n'
	spi+='SH\n'
	if rotShift != 'blank':
		spi+='%s@{*******[sel]}\n' %(stack[:-4])
		spi+='%s_parts_shifted@{*******[sel]}\n' %(outputvol)
	if rotShift == 'blank':
                spi+='%s_parts_shifted@{*******[sel]}\n' %(inputvol)
		spi+='%s_parts_shifted@{*******[sel]}\n' %(outputvol)
	spi+='-[newx],-[newy]\n'
	spi+='lb1\n'
	spi+='BP 3F\n'
	spi+='%s_parts_shifted@*******\n' %(outputvol)
	spi+='%s\n' %(workingdir)
	spi+='%s\n' %(eulers[:-4])
	spi+='*\n'
	spi+='%s\n' %(outputvol)
	spi+='FQ\n'
	spi+='%s\n' %(outputvol)
	spi+='%s_filt%03dA\n' %(outputvol,lp)
	spi+='(7)\n'
	spi+='%s,%s\n' %(str(lp1),str(lp2))
	runSpider(spi)

#==============================
def reconstruct(stack,select,eulers,apix,lp):

	lp1=(apix/lp)-0.025
	lp2=(apix/lp)+0.025

	if os.path.exists('%s' %(select[:-4])):
		print 'directory exists %s' %(select[:-4])
		shutil.rmtree('%s' %(select[:-4]))

	os.makedirs('%s' %(select[:-4]))

	spi='BP 3F\n'
	spi+='%s@*********\n' %(stack[:-4])
	spi+='%s\n' %(select[:-4])
	spi+='%s\n' %(eulers[:-4])
	spi+='*\n'
	spi+='%s/vol001\n' %(select[:-4])
        spi+='FQ\n'
	spi+='%s/vol001\n' %(select[:-4])
	spi+='%s/vol001_filt%03dA\n' %(select[:-4],lp)
	spi+='(7)\n'
	spi+='%s,%s\n' %(str(lp1),str(lp2))
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
def convertPLT_to_SPI(rotShift):

	f1=open(rotShift,'r')
	o1=open('%s.spi' %(rotShift[:-4]),'w')

	counter =1

	for line in f1:
		rot = line.split()[1]
		sx = line.split()[2]
		sy = line.split()[3]

		o1.write('%s\t3\t%s\t%s\t%s\n' %(counter,rot,sx,sy))

		counter = counter +1

#==============================
if __name__ == "__main__":

	#Imagic directory
	getEMANPath()
        imagicdir=getIMAGICPath()
	params=setupParserOptions()
        checkConflicts(params)
	
	#Create output directory
	os.mkdir(params['folder'])
	
	#Get rotation and shifts from Imagic header
	getRotShifts(params['stack'],'%s/rot_shifts.plt' %(params['folder']),imagicdir,params['debug'])
	getMembershipPerClass(params['stack'],'%s/membership.plt' %(params['folder']),imagicdir,params['debug'])

	#Create select file for each class average
	numClasses=createSpiderSelectFilesFromMembershipFile('%s/membership.plt' %(params['folder']),params['folder'],params['debug'])	

	if params['debug'] is True:
		print '\n There are %i class averages\n' %(numClasses)

	#Write spider euler angle file
	writeSpiderEulerAngles('%s/rot_shifts.plt' %(params['folder']),params['info'],'%s/euler_angles.spi' %(params['folder']),params['angle'])

	#Create a new spider stack with the 'untilted' and 'tilted' particles in alternative positions for the reconstruction
	cmd = 'e2proc2d.py %s %s/tiltMateStack.spi --first=%s --last=%s --outtype spi' %(params['stack'],params['folder'],str(getNumberOfLines(params['info'])/2),str(getNumberOfLines(params['info'])-1)) 
	if params['debug'] is True:
		print cmd
	subprocess.Popen(cmd,shell=True).wait()

	cmd = 'e2proc2d.py %s %s/tiltMateStack.spi --first=0 --last=%s --outtype spi' %(params['stack'],params['folder'],str((getNumberOfLines(params['info'])/2)-1))   
        if params['debug'] is True:
                print cmd
        subprocess.Popen(cmd,shell=True).wait()

	#Convert rotatation and shift file to spider format
	convertPLT_to_SPI('%s/rot_shifts.plt' %(params['folder']))

	#Convert euler angles to SPIDER format
	writeSpiderEulerAngles('%s/rot_shifts.plt' %(params['folder']),params['info'],'%s/euler_angles.spi' %(params['folder']),params['angle'])
	
	#Reconstruct and refine 3D volumes
	recontruct_volume_and_refine('%s/euler_angles.spi' %(params['folder']),'%s/tiltMateStack.spi' %(params['folder']),numClasses,params['folder'],params['debug'],params['lp'],params['apix'],params['radius'],'%s/rot_shifts' %(params['folder']))
