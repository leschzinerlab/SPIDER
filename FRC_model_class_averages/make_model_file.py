#!/usr/bin/env python

# usage:  ./make_model_file.py [textfile with ordered names]

import sys
import glob

file = open(sys.argv[1],'r')

i=1

for line in file:
	
	tmp=line.split()
	name = (tmp[0])
		
	print ('%s	1	%s' %(i,name))
			
	i=i+1

file.close()