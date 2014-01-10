#!/bin/csh -f

set input = $1
set reference = $2

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
/opt/qb3/imagic-110326/stand/em2em.e <<EOF
SPI
MULTIPLE_LOCATION_FILE
IM
2D
$input
${input:r}
1,1
0
EOF
echo "! "
echo "! IMAGIC program: rotate -----------------------------------------------"
echo "! "
/opt/qb3/imagic-110326/stand/rotate.e MODE EQUIV_ROTATION <<EOF
${input:r}
${reference}
${input:r}_rotated
0
BILINEAR
NO
EOF
echo "! "
echo "! IMAGIC program: em2em ------------------------------------------------"
echo "! "
/opt/qb3/imagic-110326/stand/em2em.e <<EOF
IM
SPI
MULTIPLE_LOCATION_FILE
2D
${input:r}_rotated
${input:r}_rotated.spi
LINUX
EOF
