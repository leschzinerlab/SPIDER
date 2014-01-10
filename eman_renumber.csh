#!/bin/csh

#This will take a list of numbers and add 1 to each value.  This is useful when inspecting images in EMAN and you want to know what the real number is.

set input=$1

cat $input | awk '$1 {printf ("%06.0f\n", $1+1)}' > ${input:r}_ren.txt



