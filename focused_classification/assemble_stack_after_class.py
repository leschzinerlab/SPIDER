#!/usr/bin/env python

#To run:

#./assemble_stack_after_class.py [directory] [number of classums per projection group] [output stack name]

import subprocess
import glob
import sys

directory=sys.argv[1]
num=int(sys.argv[2])
out=sys.argv[3]

list=glob.glob('%s/grp*' %(directory))

total=(len(list)+1)

for i in range(1,total):

	for n in range(0,num):

		cmd="proc2d %s/grp%03d/classums.img %s first=%s last=%s" %(directory,i,out,n,n)
		subprocess.Popen(cmd,shell=True).wait()
		
