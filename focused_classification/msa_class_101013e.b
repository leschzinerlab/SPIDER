#!/bin/csh -f

# usage:  ./msa_class_101013e.b [outputdirectory] [pixelsize] [numEIGENIM] [numCLASSES] [total#projections] [mask]

set dir=$1
set apix=$2
set numEIGEN=$3
set numCLASS=$4
set total=$5
set mask=$6

mkdir $dir

setenv IMAGIC_BATCH 1
echo "! "
echo "! "
echo "! ====================== "
echo "! IMAGIC ACCUMULATE FILE "
echo "! ====================== "
echo "! "

set i=1

while ( $i <= $total)

if($i < 10)then

mkdir $dir/grp00$i

echo "! "
echo "! IMAGIC program: em2em ------------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/stand/em2em.e <<EOF
SPI
MULT
IM
2
ali/grp00$i.spi
$dir/grp00$i/part
$apix,$apix
0
EOF
echo "! "
echo "! IMAGIC program: msa --------------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/openmpi/bin/mpirun -np 8 -x IMAGIC_BATCH  /opt/qb3/imagic-101013e/msa/msa.e_mpi <<EOF
YES
8
NO
FRESH_MSA
MODULATION
$dir/grp00$i/part
mask
$dir/grp00$i/eigenim
$dir/grp00$i/pixcoos
$dir/grp00$i/eigenpix
30
30
0.8
$dir/grp00$i/msa
EOF
echo "! "
echo "! IMAGIC program: classify ---------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/msa/classify.e <<EOF
IMAGES/VOLUMES
$dir/grp00$i/part
0
$numEIGEN
YES
$numCLASS
$dir/grp00$i/classes
EOF
echo "! "
echo "! IMAGIC program: classum ----------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/msa/classum.e <<EOF
$dir/grp00$i/part
$dir/grp00$i/classes
$dir/grp00$i/classums
YES
NONE
0
EOF

else if ( $i >= 10 && $i <= 99) then 

mkdir $dir/grp0$i

echo "! "
echo "! IMAGIC program: em2em ------------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/stand/em2em.e <<EOF
SPI
MULT
IM
2
ali/grp0$i.spi
$dir/grp0$i/part
$apix,$apix
0
EOF
echo "! "
echo "! IMAGIC program: msa --------------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/openmpi/bin/mpirun -np 8 -x IMAGIC_BATCH  /opt/qb3/imagic-101013e/msa/msa.e_mpi <<EOF
YES
8
NO
FRESH_MSA
MODULATION
$dir/grp0$i/part
mask
$dir/grp0$i/eigenim
$dir/grp0$i/pixcoos
$dir/grp0$i/eigenpix
30
30
0.8
$dir/grp0$i/msa
EOF
echo "! "
echo "! IMAGIC program: classify ---------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/msa/classify.e <<EOF
IMAGES/VOLUMES
$dir/grp0$i/part
0
$numEIGEN
YES
$numCLASS
$dir/grp0$i/classes
EOF
echo "! "
echo "! IMAGIC program: classum ----------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/msa/classum.e <<EOF
$dir/grp0$i/part
$dir/grp0$i/classes
$dir/grp0$i/classums
YES
NONE
0
EOF

else if ( $i >= 100 && $i <= $total) then 

mkdir $dir/grp$i

echo "! "
echo "! IMAGIC program: em2em ------------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/stand/em2em.e <<EOF
SPI
MULT
IM
2
ali/grp$i.spi
$dir/grp$i/part
$apix,$apix
0
EOF
echo "! "
echo "! IMAGIC program: msa --------------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/openmpi/bin/mpirun -np 8 -x IMAGIC_BATCH  /opt/qb3/imagic-101013e/msa/msa.e_mpi <<EOF
YES
8
NO
FRESH_MSA
MODULATION
$dir/grp$i/part
mask
$dir/grp$i/eigenim
$dir/grp$i/pixcoos
$dir/grp$i/eigenpix
30
30
0.8
$dir/grp$i/msa
EOF
echo "! "
echo "! IMAGIC program: classify ---------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/msa/classify.e <<EOF
IMAGES/VOLUMES
$dir/grp$i/part
0
$numEIGEN
YES
$numCLASS
$dir/grp$i/classes
EOF
echo "! "
echo "! IMAGIC program: classum ----------------------------------------------"
echo "! "
/opt/qb3/imagic-101013e/msa/classum.e <<EOF
$dir/grp$i/part
$dir/grp$i/classes
$dir/grp$i/classums
YES
NONE
0
EOF

endif

@ i++

end
