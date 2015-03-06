#!/usr/bin/env python

import sys 

#=============================
def convert_box_to_spi(boxfile):

        f1 = open(boxfile,'r')

        o1 = open('%s_picks.spi' %(boxfile[:-4]),'w')

        count = 1

        for line in f1:
                l = line.split()

                x = float(l[0])
                y = float(l[1])
                box = float(l[2])/2

                o1.write('%i\t4\t%i\t%f\t%f\t1\n' %(count,count,x+box,y+box))
                count = count + 1

        return box
#==============================
def convert_spi_to_box(boxfile,boxsize):

        o1 = open('%s_out.box'%(boxfile[:-4]),'w')

        f1 = open(boxfile,'r')

        for line in f1:

                if line[1] == ';':
                        continue

                l = line.split()

                x = float(l[3])-boxsize/2
                y = float(l[4])-boxsize/2

                o1.write('%i\t%i\t%i\t%i\t-3\n' %(int(x),int(y),int(boxsize),int(boxsize)))
#==============================
if __name__ == "__main__":
	
	#convert_box_to_spi('../14sep22z_14sep20a_00015hl_00_00012en_00.box')
	boxsize = int(sys.argv[1])

	convert_spi_to_box('output/final_unt_coordinates_00286.spi',boxsize)
	convert_spi_to_box('output/final_tlt_coordinates_00286.spi',boxsize)
