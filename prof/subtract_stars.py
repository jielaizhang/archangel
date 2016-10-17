#!/usr/bin/env python

import pyfits, sys, random, os, os.path
from xml_archangel import *
from math import *

if '-h' in sys.argv:
  print 'subtract_stars op cleaned_file (sigma)'
  print 
  print 'fills the clean areas with random noise'
  print 'options:  -s = add random sky to cleaned areas'
  print '          -c = use areas from cleaned file'
  print '          -b = boxcar smooth'
  sys.exit()

try:
  sigma=float(sys.argv[-1])
  filename=sys.argv[-2]
except:
  sigma=10.
  filename=sys.argv[-1]

file=pyfits.open(filename.split('.')[0]+'.fake')
data1=file[0].data
file=pyfits.open(filename.split('.')[0]+'.clean')
data2=file[0].data

doc = minidom.parse(filename.split('.')[0]+'.xml')
rootNode = doc.documentElement
elements=xml_read(rootNode).walk(rootNode)
sky=float(elements['sky'][0][1])

sigma=sigma*float(elements['skysig'][0][1])

nx=file[0].header['NAXIS1']
ny=file[0].header['NAXIS2']

for j in range(ny):
  for i in range(nx):
    x=random.random()
    y=random.random()
    c=sigma*(sqrt(-2.*log(x)))*(cos(2.*pi*y))
    if '-s' in sys.argv and str(data1[j][i]) == 'nan':
      data1[j][i]=sky+c
    elif str(data2[j][i]) == 'nan':
      data1[j][i]=data1[j][i]+c

if '-b' in sys.argv:
  for j in range(2,ny-2,1):
    for i in range(2,nx-2,1):
      if str(data2[j][i]) == 'nan':
        avg=data1[j-1][i-1]+data1[j][i-1]+data1[j+1][i-1]
        avg=avg+data1[j-1][i]+data1[j][i]+data1[j+1][i]
        avg=avg+data1[j-1][i+1]+data1[j][i+1]+data1[j+1][i+1]
        data1[j][i]=avg/9.

if '-s' not in sys.argv and '-c' not in sys.argv:
  file=pyfits.open(filename)
  data2=file[0].data
  data3=data2-data1

if os.path.isfile(filename.split('.')[0]+'.stars'): os.remove(filename.split('.')[0]+'.stars')
fitsobj=pyfits.HDUList()
hdu=pyfits.PrimaryHDU()
hdu.header=file[0].header
if '-s' in sys.argv or '-c' in sys.argv:
  hdu.data=data1
else:
  hdu.data=data3
fitsobj.append(hdu)
fitsobj.writeto(filename.split('.')[0]+'.stars')
