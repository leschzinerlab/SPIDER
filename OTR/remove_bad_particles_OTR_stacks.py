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
        parser.set_usage("%prog -u <stack.img> -t <stack.img> --untiltCTF=<file> --tiltCTF=<file> --box=<box> --radius=<radius>")
        parser.add_option("-u",dest="untilt",type="string",metavar="FILE",
                help="Untilted particle stack")
	parser.add_option("-t",dest="tilt",type="string",metavar="FILE",
                help="Tilted particle stack")
        parser.add_option("--untiltCTF",dest="untiltCTF",type="string", metavar="FILE",
                help="CTFTILT file for untilted particles")
	parser.add_option("--tiltCTF",dest="tiltCTF",type="string", metavar="FILE",
                help="CTFTILT file for tilted particles")
	parser.add_option("--box",dest="boxsize",type="int", metavar="INT",
                help="Box size of particles")
	parser.add_option("--radius",dest="radius",type="int", metavar="INT",
                help="Tilted particles that fall outside of this radius will be excluded (pixels)")
	parser.add_option("-d", action="store_true",dest="debug",default=False,
                help="debug")
        options,args = parser.parse_args()

        if len(args) > 0:
                parser.error("Unknown commandline options: " +str(args))

        if len(sys.argv) < 4:
                parser.print_help()
                sys.exit()
        params={}
        for i in parser.option_list:
                if isinstance(i.dest,str):
                        params[i.dest] = getattr(options,i.dest)
        return params

#=============================
def checkConflicts(params):
	if params['untilt'][-4:] != '.img':
			if params['untilt'][-4:] != '.hed':
				print 'Stack extension %s is not recognized as .hed or .img file' %(params['untilt'][-4:])
				sys.exit()
	if params['tilt'][-4:] != '.img':
			if params['tilt'][-4:] != '.hed':
				print 'Stack extension %s is not recognized as .hed or .img file' %(params['tilt'][-4:])
				sys.exit()
	if not os.path.exists(params['tilt']):
		print 'Stack %s does not exist. Exiting.' %(params['tilt'])
		sys.exit()

	if not os.path.exists(params['untilt']):
		print 'Stack %s does not exist. Exiting.' %(params['untilt'])
		sys.exit()

	if os.path.exists('%s_sel.img' %(params['tilt'][:-4])):
		print 'Output stack %s_sel.img exists. Exiting.' %(params['tilt'][:-4])
		sys.exit()

	if os.path.exists('%s_sel.img' %(params['untilt'][:-4])):
		print 'Output stack %s_sel.img exists. Exiting.' %(params['untilt'][:-4])
		sys.exit()

	if not os.path.exists(params['tiltCTF']):
		print 'File %s does not exist. Exiting.' %(params['tiltCTF'])
		sys.exit()

	if not os.path.exists(params['untiltCTF']):
		print 'File %s does not exist. Exiting.' %(params['untiltCTF'])
		sys.exit()

	if os.path.exists('%s_sel.txt' %(params['tiltCTF'][:-4])):
		print 'Output file %s_sel.txt already exists. Exiting.' %(params['tiltCTF'][:-4])
		sys.exit()
	if os.path.exists('%s_sel.txt' %(params['untiltCTF'][:-4])):
		print 'Output file %s_sel.txt already exists. Exiting.' %(params['untiltCTF'][:-4])
		sys.exit()

	if params['radius'] > params['boxsize']: 
		print 'Radius %i > Box %i. Exiting.' %(params['radius'],params['boxsize'])
		sys.exit()

	if getNumLines(params['tiltCTF']) != getNumLines(params['untiltCTF']):
		print '%s and %s files have different numbers of line entries. Exiting.' %(params['tiltCTF'],params['untiltCTF'])
		sys.exit()

	if os.path.exists('%s.spi' %(params['untilt'][:-4])):
		print '%s.spi already exists. Exiting.' %(params['untilt'][:-4])
		sys.exit()
	
	if os.path.exists('%s.spi' %(params['tilt'][:-4])):
		print '%s.spi already exists. Exiting.' %(params['tilt'][:-4])
		sys.exit()
	

#==============================
def getNumLines(f1):
	tot=len(open(f1,'r').readlines())
	return tot

#==============================
def convertIMG_to_SPI(f1,debug):

	cmd = 'proc2d %s %s.spi spiderswap' %(f1,f1[:-4])
	if debug is True:
		print '\n%s\n' %(cmd)
	subprocess.Popen(cmd,shell=True).wait()

#==============================
def compare_tilt_untilt_particles_SPI(untilt,tilt,radius,boxsize,totlines):

	if os.path.exists('tmp_bad_particles.spi'):
		os.remove('tmp_bad_particles.spi')

	if os.path.exists('%s_BadParts.spi' %(untilt)):
		os.remove('%s_BadParts.spi' %(untilt))

	spicmd='MS\n'
	spicmd+='_9@\n'	
	spicmd+='%s,%s,1\n' %(str(boxsize),str(boxsize))
	spicmd+='%s\n' %(str(totlines))
	spicmd+='[counter]=1\n'
	spicmd+='MS\n'
	spicmd+='_8@\n'
	spicmd+='%s,%s,1\n'%(str(boxsize),str(boxsize))
	spicmd+='%s*3\n'%(str(totlines))
	spicmd+='SD IC NEW\n'
	spicmd+='incore\n'
	spicmd+='1,%s\n'%(str(totlines))
	spicmd+='SD IC NEW\n'
	spicmd+='incore2\n'
	spicmd+='3,%s\n'%(str(totlines))
	spicmd+='[loop]=1\n'
	spicmd+='do lb1 [part]=1,%s\n' %(str(totlines))
	spicmd+='[flag]=0\n'
        spicmd+='FS [max] [min] [avg1] [std1]\n'
        spicmd+='%s@{********[part]}\n'%(untilt)
        spicmd+='AR\n'
        spicmd+='%s@{*******[part]}\n'%(untilt)
        spicmd+='_2\n'
        spicmd+='P1-[avg1]/[std1]\n'
	spicmd+='FS [max] [min] [avg1] [std1] \n'
	spicmd+='%s@{********[part]}\n'%(tilt)
	spicmd+='AR\n'
	spicmd+='%s@{*******[part]}\n'%(tilt)
	spicmd+='_1\n'
	spicmd+='P1-[avg1]/[std1]\n'
	spicmd+='CC N\n'
	spicmd+='_1\n'
	spicmd+='_2\n'
	spicmd+='_9@{*******[part]}\n'
	spicmd+='PK M  [x],[y],[xo],[yo],[pk]\n'
	spicmd+='_9@{*******[part]}\n'
	spicmd+='\n'
	spicmd+='[mid1]=(%s/2)+%s\n' %(str(boxsize),str(radius))
	spicmd+='[mid2]=(%s/2)-%s\n' %(str(boxsize),str(radius))
	spicmd+='IF([min].EQ.0) THEN\n'
	spicmd+='	[flag]=1\n'
	spicmd+='ENDIF\n'
	spicmd+='IF([x].GT.[mid1]) THEN\n'
	spicmd+='	[flag]=1\n'
	spicmd+='ENDIF\n'
	spicmd+='IF([x].LT.[mid2]) THEN\n'
        spicmd+='        [flag]=1\n'
        spicmd+='ENDIF\n'
        spicmd+='IF([y].GT.[mid1]) THEN\n'
        spicmd+='        [flag]=1\n'
        spicmd+='ENDIF\n'
        spicmd+='IF([y].LT.[mid2]) THEN\n'
        spicmd+='        [flag]=1\n'
        spicmd+='ENDIF	\n'
	spicmd+='IF([flag].EQ.1) THEN\n'
	spicmd+='[loop2]=[loop]+1\n'
	spicmd+='[loop3]=[loop2]+1\n'
	spicmd+='CP\n'
	spicmd+='_2\n'
	spicmd+='_8@{*******[loop]}\n'
	spicmd+='CP\n'
	spicmd+='_1\n'
	spicmd+='_8@{*******[loop2]}\n'
	spicmd+='CP\n'
        spicmd+='_9@{*******[part]}\n'
        spicmd+='_8@{*******[loop3]}\n'
	spicmd+='SD IC [counter] [part]\n'
	spicmd+='incore\n'
	spicmd+='[loop]=[loop]+3\n'
	spicmd+='[counter]=[counter]+1\n'
	spicmd+='ENDIF\n'
	spicmd+='lb1\n'
	spicmd+='DE \n'
	spicmd+='_9@\n'
	spicmd+='SD IC COPY\n'
	spicmd+='incore\n'
	spicmd+='tmp_bad_particles\n'
	spicmd+='CP\n'
	spicmd+='_8@\n'
	spicmd+='%s_BadParts@\n' %(untilt)
	spicmd+='DE\n'
	spicmd+='_8@\n'
        runSpider(spicmd)

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
def spi_file_to_txt(f1,out):

	if os.path.exists('%s_BadParts.txt' %(out)):
		os.remove('%s_BadParts.txt' %(out))

	f = open(f1,'r')
	o = open('%s_BadParts.txt' %(out),'w')
	for line in f:
		if line[1] == ';':
			continue		
		l = line.split()
		part = str(float(l[2])-1)
		o.write('%s\n' %(part))

	o.close()
	f.close()

#==============================
def remove_bad_parts_files(f1,badlist,debug):

	counter=1

	f = open(f1,'r')
	o = open('%s_sel.txt' %(f1[:-4]),'w')

	for line in f: 

		badf1 = open(badlist,'r')
		flag=0
		for line2 in badf1:
			l2=line2.split()
			if float(l2[0]) == (counter-1):
				flag=1
				if debug is True:
					print 'Particle %s is bad (EMAN numbering)' %(str(counter-1))
		
		badf1.close()

		if flag > 0: 
			if debug is True:
				print 'Skipping particle %s' %(str(counter-1))
				counter = counter + 1
				continue

		o.write(line)
		counter = counter + 1

	o.close()
	f.close()


#==============================
if __name__ == "__main__":

	params=setupParserOptions()
        checkConflicts(params)
	
	#Convert stacks to SPIDER format
	convertIMG_to_SPI(params['untilt'],params['debug'])
	convertIMG_to_SPI(params['tilt'],params['debug'])	

	#Run spider alignment script
	compare_tilt_untilt_particles_SPI(params['untilt'][:-4],params['tilt'][:-4],params['radius'],params['boxsize'],getNumLines(params['untiltCTF']))

	#Write spider 'bad' particle list into format for proc2d
	spi_file_to_txt('tmp_bad_particles.spi',params['untilt'][:-4])

	#Remove bad particles from each stack	
	cmd = 'proc2d %s %s_sel.img exclude=%s_BadParts.txt' %(params['untilt'],params['untilt'][:-4],params['untilt'][:-4])
	if params['debug'] is True:
		print cmd
	subprocess.Popen(cmd,shell=True).wait()

	cmd = 'proc2d %s %s_sel.img exclude=%s_BadParts.txt' %(params['tilt'],params['tilt'][:-4],params['untilt'][:-4])
	if params['debug'] is True:
		print cmd
	subprocess.Popen(cmd,shell=True).wait()
	
	#Remove bad particles from ctftilt files
	remove_bad_parts_files(params['untiltCTF'],'%s_BadParts.txt' %(params['untilt'][:-4]),params['debug'])
	remove_bad_parts_files(params['tiltCTF'],'%s_BadParts.txt' %(params['untilt'][:-4]),params['debug'])

	#Clean up
	if params['debug'] is False:
		os.remove('%s_BadParts.spi' %(params['untilt']))
		os.remove('tmp_bad_particles.spi')
		os.remove('%s.spi' %(params['untilt'][:-4]))
		os.remove('%s.spi' %(params['tilt'][:-4]))
		
