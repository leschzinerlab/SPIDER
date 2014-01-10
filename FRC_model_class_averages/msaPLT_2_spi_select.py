#!/usr/bin/env python

# usage:  ./msaPLT_2_spi_select.py [msaPLTfile].plt [numClasses]

import sys
import glob
import os

file = sys.argv[1]
num = int(sys.argv[2])+1
one=1
i=1
f=open(file,'r')
l = f.readlines()

for i in range(1,num):
	
	h=1
	j=1
	
	fout=('class_%03d.spi' %(i))
	fout=open(fout,'a')
	for line in l:
		
		tmp=line.split()
		tmp2=float(tmp[0])
		
		if i == tmp2:
			fout.write('%s       1	       %s\n' %(j,h))
			j=j+1
			
		h = h + 1
		
	fout.close()	

f.close()




