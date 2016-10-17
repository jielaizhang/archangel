#!/usr/bin/env python

import sys
import numpy.numarray as numarray
from xml_archangel import *
from math import *

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

def findr(t,eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  c1=bsq*(cos(t))**2+asq*(sin(t))**2
  c2=(asq-bsq)*2*sin(t)*cos(t)
  c3=bsq*(sin(t))**2+asq*(cos(t))**2
  c4=asq*bsq
  return (c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**0.5

if '-h' in sys.argv:
  print ' '
  print 'Usage: pixel_isophote xml_prefix x y'
  print
  print 'returns isophotal value at x,y, -sfb in sfb units'
  sys.exit()

xc=float(sys.argv[-2])
yc=float(sys.argv[-1])

k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05}

doc = minidom.parse(sys.argv[-3].split('.')[0]+'.xml')
rootNode = doc.documentElement
elements=xml_read(rootNode).walk(rootNode)
scale=float(elements['scale'][0][1])
exptime=float(elements['exptime'][0][1])
airmass=float(elements['airmass'][0][1])
sky=float(elements['sky'][0][1])
zpt=float(elements['zeropoint'][0][1])
filter=elements['filter'][0][1]

for t in elements['array']:
  if t[0]['name'] == 'prf':
    prf=[]
    for z in t[2]['axis']:
      prf.append(map(float,z[1].split('\n')))
    tmp=numarray.array(prf)
    prf=numarray.swapaxes(tmp,1,0)
    break

for n,z in enumerate(prf[1:]):
# note, look at n cause we skip the first one
  t=atan((yc-z[14])/(xc-z[15]))
  rr=((xc-z[14])**2.+(yc-z[15])**2.)**0.5
  r2=findr(t,1.-z[12],z[3],-z[13]*pi/180.,z[14],z[15])
  r1=findr(t,1.-prf[n][12],prf[n][3],-prf[n][13]*pi/180.,prf[n][14],prf[n][15])
#  print rr,r1,r2,prf[n][3],z[3]
  if rr < r2:
    t=atan((yc-prf[n][14])/(xc-prf[n][15]))
    r1=findr(t,1.-prf[n][12],prf[n][3],-prf[n][13]*pi/180.,prf[n][14],prf[n][15])
#    print r1,r2,prf[n][0],z[0],rr,prf[n][3],z[3]
    if '-sfb' in sys.argv:
      mag=interp(r1,r2,prf[n][0],z[0],rr)
      print sys.argv[-3],
      try:
        print -2.5*log10((mag-sky)/(scale*scale*exptime))-k[filter]*airmass+zpt
      except:
        print 'math error'
    else:
      print interp(r1,r2,prf[n][0],z[0],rr)
    break
else:
  print 'beyond last isophote, sky =',
  try:
    print elements['sky'][0][1]
  except:
    print 'unknown'
