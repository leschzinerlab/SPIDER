#!/bin/csh

#This will take all inputs within a given file and copy to a new folder all of the exposures & high defocus focal pairs into a separate folder

#For this batch, the exposures & ef (focal pair image at high defocus) have the same file name except for the last bit before the extension.

set data =  /leginon2/michael/11oct22a/rawdata/

#Reads in the file name for the focal pair
foreach file (*en.box)

#Removes the extension so that the same base filename can be used to copy the expose.mrc file
set new=`echo $file | sed -e 's/en.box//'`

ln -s $data/${new}en.mrc .

ln -s $data/${new}ef.mrc .

end 





