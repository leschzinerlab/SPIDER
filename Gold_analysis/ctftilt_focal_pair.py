#!/usr/bin/env python

#This script expects that tilt pair micrographs are named in Leginon format.

#Output filenames
paramOUT1 = 'parameter_en.par'	#param filename for untilted particles
paramOUT2 = 'parameter_ef.par'	#param filename for tilted particles
stack1 = 'stack_en'		#stack name for untilted particles
stack2 = 'stack_ef'		#stack name for tilted particles

#Inputs
shrink = 4			#Binning factor for final particle stack
new = 100			#Box size for binned particles
scale = 1			#Binning factor used for micrograph from which the particles were picked

#CTFTILT inputs
parm3 = "2.2,120.0,0.07,80000,12.03141,2\n" # !CS[mm],HT[kV],AmpCnst,XMAG,DStep[um]

#Parameter inputs for 00.mrc micrographs
parm4 = "128,400.0,8.0,20000.0,65000.0,500.0,0,0,5\n" #!Box,ResMin[A],ResMax[A],dFMin[A],dFMax[A],FStep,Expected angle, step size

#Parameter inputs for 01.mrc micrographs
parm5 = "128,400.0,8.0,1000.0,35000.0,500.0,0,0,5\n" #!Box,ResMin[A],ResMax[A],dFMin[A],dFMax[A],FStep,Expected angle, step size

#############		Script		###############

import subprocess
import sys
import re
import os
import glob

p1 = open(paramOUT1,'wa')
p2 = open(paramOUT2,'wa')
cmd = "/archive/glander/myami/appion/bin/ctftilt64.exe"

#syntax: grep(regexp_string,list_of_strings_to_search)
def grep(string,list):
        expr = re.compile(string)
        return filter(expr.search,list)

list = glob.glob('*en.box.new2')

micro  = 1
particle1 = 1
particle2 = 1

o1 = open('micrograph_list.txt','w')

for file in list: 
       	
	ef = '%sef.box2' %(file[:-11])
	#Check if both files exist
	if os.path.isfile(file) & os.path.isfile(ef):
               	
		o1.write('%s	%s	%s\n' %(str(micro),file, ef))

		mrcEN = '%s.mrc' %(file[:-9])
		mrcEF = '%s.mrc' %(ef[:-5])
		
		a = subprocess.Popen(cmd, -1, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		[o,e] = a.communicate('%s\n'%(mrcEN) + '%s.diag\n'%(mrcEN) + parm3 + parm4)
		out = grep("Final Values", o.split("\n"))
		out2 = out[0]
		out3 = out2.split()
		
       		b = open(file)
        	tot = len(b.readlines())
        	i = 1
        
        	while i <= tot:
	
			p1.write('%s		%s		%s		%s	%s	%s\n' %(out3[0],out3[1],out3[2],out3[4],str(particle1),str(micro)))
			particle1 = particle1 + 1
			i = i + 1

		cmd2 = 'batchboxer input=%s dbbox=%s scale=%s output=%s.img' %(mrcEN,file,scale,stack1)
		subprocess.Popen(cmd2,shell=True).wait()

		a = subprocess.Popen(cmd, -1, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                [o,e] = a.communicate('%s\n'%(mrcEF) + '%s.diag\n'%(mrcEF) + parm3 + parm5)
                out = grep("Final Values", o.split("\n"))
                out2 = out[0]
                out3 = out2.split()

                b = open(ef)
                tot = len(b.readlines())
                i = 1

                while i <= tot:

                        p2.write('%s    	%s      	%s      	%s	%s	%s\n' %(out3[0],out3[1],out3[2],out3[4],str(particle2),str(micro)))
			particle2 = particle2 + 1
                        i = i + 1

                cmd2 = 'batchboxer input=%s dbbox=%s scale=%s output=%s.img' %(mrcEF,ef,scale,stack2)
                subprocess.Popen(cmd2,shell=True).wait()

		micro = micro + 1

cmd3 = 'proc2d %s.img %s_dc%01d.img meanshrink=%s' %(stack1,stack1,float(shrink),shrink)
subprocess.Popen(cmd3,shell=True).wait()

cmd4 = 'proc2d %s_dc%01d.img %s_dc%01d_edgenorm.img edgenorm=0,1' %(stack1,float(shrink),stack1,float(shrink))
subprocess.Popen(cmd4,shell=True).wait()

cmd3 = 'proc2d %s.img %s_dc%01d.img meanshrink=%s' %(stack2,stack2,float(shrink),shrink)
subprocess.Popen(cmd3,shell=True).wait()

cmd4 = 'proc2d %s_dc%01d.img %s_dc%01d_edgenorm.img edgenorm=0,1' %(stack2,float(shrink),stack2,float(shrink))
subprocess.Popen(cmd4,shell=True).wait()
