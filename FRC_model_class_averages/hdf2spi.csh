#!/bin/csh -f

#Usage:  ./hdf2spi.csh

foreach file (*.hdf)

set new = ${file:r}

proc3d $file ${new}.img imagic

setenv IMAGIC_BATCH 1
echo "! "
echo "! "
echo "! ====================== "
echo "! IMAGIC ACCUMULATE FILE "
echo "! ====================== "
echo "! "
echo "! "
echo "! IMAGIC program: em2em ------------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/stand/em2em.e <<EOF
IMAGIC
SPI
MULTIPLE_LOCATION_FILE
3
$new
${new}.spi
LINUX
YES
EOF

end

rm *.img rm *.hed

