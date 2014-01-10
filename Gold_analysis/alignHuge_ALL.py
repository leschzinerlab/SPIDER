#!/usr/bin/env python

import os
import shutil
import glob
import re
import subprocess

list = glob.glob("*en.mrc")

for en in list:
	
	ef = re.sub("en","ef",en)
	efAli = re.sub("en","efAli",en)

	cmd='proc2d %s %s_filt.mrc apix=1.501 lp=20' %(ef,ef[:-4])
	subprocess.Popen(cmd,shell=True).wait()

	cmd="alignhuge %s_filt.mrc %s %s" %(ef[:-4],en,efAli)
	subprocess.Popen(cmd,shell=True).wait()

	cmd='rm %s_filt.mrc %s' %(ef[:-4],efAli)
	subprocess.Popen(cmd,shell=True).wait()
