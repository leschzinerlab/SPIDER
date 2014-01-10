#!/bin/csh 

#To run:  ./rename_hdf2spi.csh [HDF volume extension to replace]

#For example: if I have volf_025_04.spi, volf_023_04.spi, volf_020_04.spi, etc. that I want to use, then:
# ./rename_hdf2spi.csh 04

set vol=$1

foreach file (volf_???_${vol}.spi)

set new=`echo $file | sed -e 's/_'${vol}'.spi//'`

ln -s $file ${new}.spi

end
