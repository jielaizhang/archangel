#!/usr/bin/env python

# this script cleans off nonsense values, i.e. for those files which do not
# use NaN for useless pixels

import sys,os
import astropy.io.fits as pyfits
from math import *

# open file, find prefix, cleaned file will be written out as .raw

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: clean_blanks option filename number'
  print
  print 'Options: -h = this message'
  print '         -c = set all bad pixels to NaN'
  print '         -s = search for bad pixels and display'
  print '         number = number of occurances to kill'
  sys.exit()
else:
  if '.' not in sys.argv[2]: print 'bad filename, aborting' ; sys.exit()
  prefix=sys.argv[2].split('.')[0]
  endfix=sys.argv[2].split('.')[1]

if len(sys.argv) > 3:
  num=int(sys.argv[-1])
else:
  num=100

fitsobj=pyfits.open(prefix+'.'+endfix,'readonly')
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
hdr=fitsobj[0].header
pix=fitsobj[0].data

# sort pixels into dictionary

u={}
for x in pix.flat:
  if x == x:
    if u.has_key(x):
      u[x]=u[x]+1
    else:
      u[x]=1

# find the multiple occurrences of *exactly* same number, if greater than num, add to bad list

bad=[]
for x in u.keys():
  if u[x] > num: bad.append(x)
for x in bad:
  if str(x) == 'nan': del bad[bad.index(x)]

if sys.argv[1] == '-c':

# kill all pixels on bad list

  if len(bad) != 0:
    for j in range(ny):
      for i in range(nx):
        if pix[j,i] in bad: pix[j,i]=float('nan')

# write me out

  if os.path.isfile(prefix+'.raw'): os.remove(prefix+'.raw')
  fitsobj2=pyfits.HDUList()
  hdu=pyfits.PrimaryHDU()
  hdu.header=fitsobj[0].header
  hdu.data=pix
  fitsobj2.append(hdu)
  fitsobj2.writeto(prefix+'.raw')

else:
  for x in bad:
    print 'Value',x,'had',u[x],'occurances'
