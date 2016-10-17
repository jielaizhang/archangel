#!/usr/bin/env python

import os, sys, pyfits

if len(sys.argv) == 1:
  tmp=os.popen('ls *.fits').read()
else:
  tmp=os.popen('ls '+sys.argv[-1]+'.fits').read()
files=tmp.split('\n')[:-1]
max=0
for file in files:
  if len(file) > max: max=len(file)
for file in files:
  fitsobj=pyfits.open(file,"readonly")
  print file.ljust(max),
  print '%6.0i' % int(fitsobj[0].header['EXPTIME']),
#  print '%5.2f' % float(fitsobj[0].header['AIRMASS']),
  print fitsobj[0].header['OBJECT'].ljust(15),
  print fitsobj[0].header['DATE-OBS']
