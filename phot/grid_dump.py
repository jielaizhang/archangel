#!/usr/bin/env python

import sys, os, math
try:
  import numpy.numarray as numarray
except:
  import numarray
from xml_archangel import *
import astropy.io.fits as pyfits

if sys.argv[1] == '-h' or len(sys.argv) < 2:
  print 'grid_dump op thres data_file'
  print
  print 'dumps data points marks in xml file'
  print
  print 'options: -t = dump all above threshold'
  print '         -m = use marks.tmp for marks'
  print '         -b = average 3x3'
  sys.exit()

fitsobj=pyfits.open(sys.argv[-1],"readonly")
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()

if '-t' in sys.argv:
  nx=fitsobj[0].header['NAXIS1']
  ny=fitsobj[0].header['NAXIS2']
  for j in range(ny):
    for i in range(nx):
      if pix[j][i] > float(sys.argv[2]): print i+1,j+1,pix[j][i]

else:
  if '-m' in sys.argv:
    marks=[map(float,tmp.split()) for tmp in open('marks.tmp','r').readlines()]
  else:
    try:
      doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
      rootNode = doc.documentElement
      elements=xml_read(rootNode).walk(rootNode)
      for t in elements['array']:
        if t[0]['name'] == 'marks': # ellipse data
          marks=[]
          head=[]
          pts=[]
          for z in t[2]['axis']:
            head.append(z[0]['name'])
            pts.append(map(float,z[1].split('\n')))
          for z in range(len(pts[0])):
            tmp=[]
            for w in head:
              tmp.append(pts[head.index(w)][z])
            marks.append(tmp)
    except:
      print 'no marks in xml file'
      sys.exit()

  if '-b' in sys.argv:
    for i,j in marks:
      tmp=0. ; n=0.
      for ii in [-1,0,1]:
        for jj in [-1,0,1]:
          if pix[int(round(j+jj))-1][int(round(i+ii))-1] == pix[int(round(j+jj))-1][int(round(i+ii))-1]:
            n=n+1.
            tmp=tmp+pix[int(round(j+jj))-1][int(round(i+ii))-1]
      print int(round(i)),int(round(j)),tmp/n
  else:
    for i,j in marks:
      print int(round(i)),int(round(j)),pix[int(round(j))-1][int(round(i))-1]
