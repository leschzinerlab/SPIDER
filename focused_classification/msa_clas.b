#!/bin/csh -f

# This batch will go into the grp*** folders that are the outputs of b98.grp and classify the particles using MSA

setenv IMAGIC_BATCH 1
echo "! "
echo "! "
echo "! ====================== "
echo "! IMAGIC ACCUMULATE FILE "
echo "! ====================== "
echo "! "
echo "! "

set i=10

while ( $i <= 46 )

mkdir 3_classes/grp0$i

echo "! IMAGIC program: em2em ------------------------------------------------"
echo "! "
/usr/local/imagic-070813/stand/em2em.e <<EOF
SPIDER
SINGLE_FILE
IMAGIC
2D
ali/grp0$i
spi
3_classes/grp0$i/part
4.56,4.56,4.56
EOF
echo "! "
echo "! IMAGIC program: msa --------------------------------------------------"
echo "! "
/usr/local/imagic-070813/msa/msa.e <<EOF
FRESH_MSA
MODULATION
3_classes/grp0$i/part
NO
../MASK_VAR_20_di2/prjmsk,$i
3_classes/grp0$i/eigenim
3_classes/grp0$i/pixcoos
3_classes/grp0$i/eigenpix
24
10
0.8
3_classes/grp0$i/msa
EOF
echo "! "
echo "! IMAGIC program: classify ---------------------------------------------"
echo "! "
/usr/local/imagic-070813/msa/classify.e <<EOF
IMAGES
3_classes/grp0$i/part
0
10
YES
3
3_classes/grp0$i/classes
EOF
echo "! "
echo "! IMAGIC program: classum ----------------------------------------------"
echo "! "
/usr/local/imagic-070813/msa/classum.e <<EOF
3_classes/grp0$i/part
3_classes/grp0$i/classes
3_classes/grp0$i/classums
YES
NONE
0
EOF
@ i++

end
