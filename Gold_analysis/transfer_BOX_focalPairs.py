#!/usr/bin/env python

#This will apply the shifts & transformations calculated by alignHuge_ALL.py (found in alignhuge.txt) to the box file for en,
#outputting [micro]ef.box files

#To run:

#   ./transfer_BOX_focalPairs.py alignhuge.txt

import glob
import re
import os
import sys
import shutil

input=sys.argv[1]
file=open(input)

for line in file:
	
	tmp=line.rsplit()
	ef1 = tmp[0]
	en1 = tmp[1]
	shx1 = tmp[2]
	shy1 = tmp[3]
		
	ef = ef1.strip(',')	
	en = en1.strip(',')
	shx = int(shx1.strip(','))
	shy = int(shy1.strip(','))

	enBox = ('%s.box' %(en))
	efBox = ('%s.box' %(ef[:-5]))
	
	test = os.path.exists(enBox)
	
	if test is True:
			
		box = open(enBox,'r')
		newBox = open(efBox,'w')
		#newEnBox = open(enBox+".new2",'w')
		
		#calculate new shifts & make sure that particles are within bounds of micrograph
		
		for entry in box:
			
			num = entry.rsplit()
			
			enX=int(num[0])
			enY=int(num[1])
			size=int(num[2])
			place = int(num[4])
			
			limit1 = 4096 - size
			limit2 = 0 + size
			#coordinate is lower left
			
			#if limit2 < enX < limit1 and limit2 < enY < limit1:
						
			efX = enX - shx
			efY = enY - shy
			
			#	if limit2 < efX < limit1 and limit2 < efY < limit1:
					
			newBox.write("%s	%s	%s	%s	%s \n"%(efX,efY,size,size,place))
			#newEnBox.write("%s	%s	%s	%s	%s \n"%(enX,enY,size,size,place))
			#	else:
					
			#		print ("EF particle is out of bounds:  X:%s, Y:%s" %(efX, efY))
			#else:
			
			#	print ("EN particle out of bounds:  X:%s, Y:%s" %(enX,enY))
			
			
			
			
			
			
			
		box.close()
		newBox.close()
	
	
		
