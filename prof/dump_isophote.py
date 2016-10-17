#!/usr/bin/env python

# elliptical apertures, manual version of elapert
# note that python array coords and IRAF coords are off
# by one pixel x/y and flipped; e.g. data(i,j) == pix[j-1][i-1]

# the ecc and pos angle for an ellipse will look on a frame that
# is plotted 0,0 in lower left corner such that a p.a. of 45
# will point the minor axis to 10:30, the major axis to 2:30
# as the p.a. goes to zero, minor axis goes towards 12:00, as
# p.a. goes negative, minor axis points towards 1:00 etc.

# also note, taking area from gasp_images is only a/2 and b/2

import sys, os
from math import *
try:
  import numpy.numarray as numarray
except:
  import numarray
import astropy.io.fits as pyfits
from xml_archangel import *
import warnings ; warnings.simplefilter('ignore')

def findr(t,eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  c1=bsq*(cos(t))**2+asq*(sin(t))**2
  c2=(asq-bsq)*2*sin(t)*cos(t)
  c3=bsq*(sin(t))**2+asq*(cos(t))**2
  c4=asq*bsq
  return (c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**0.5

# main

if sys.argv[1] == '-h':
  print 'dump_isophote options fits_file r_annulus xc yc a b theta'
  print ' or'
  print 'dump_isophote options fits_file r_annulus xc yc major_axis eps=(1-b/a) theta'
  print
  print 'options:   -h = this message'
  print '           -m = print pixels used (marks)'
  print '           -g = use gasp_images output (s.tmp)'
  sys.exit()

if '-g' in sys.argv:
  ifile=-2
else:
  ifile=-7

fitsobj=pyfits.open(sys.argv[ifile],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
aspect=1.
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()

if '-g' in sys.argv:
  file=open('s.tmp','r')
  lines=[]
  while 1:
    l=file.readline().split()
    if not l: break
    a=(float(l[2])/(pi*(1.-float(l[3]))))**0.5
    lines.append([0.,1.,2.,a,4.,5.,6.,7.,8.,9.,10.,11.,float(l[3]),float(l[-2]),float(l[0]),float(l[1])])

else:
  if float(sys.argv[-2]) <= 1.:
    eps=float(sys.argv[-2])
  else:
    eps=1.-(float(sys.argv[-2])/float(sys.argv[-3]))

  lines=[[0.,1.,2.,float(sys.argv[-3]),4.,5.,6.,7.,8.,9.,10.,11.,eps,float(sys.argv[-1]),float(sys.argv[-5]),float(sys.argv[-4])]]

if os.path.exists(sys.argv[ifile].split('.')[0]+'.xml'):
  doc = minidom.parse(sys.argv[ifile].split('.')[0]+'.xml')
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)

  try:
    zpt=float(elements['zeropoint'][0][1])
  except:
    zpt=0.

  try:
    xsky=float(elements['sky'][0][1])
  except:
#    print 'sky value not found, setting to zero'
    xsky=0.
  try:
    skysig=float(elements['skysig'][0][1])
  except:
#    print 'skysig not found, setting to one'
    skysig=1.

  if '-sky' in sys.argv:
    xsky=float(sys.argv[sys.argv.index('-sky')+1])

rr=float(sys.argv[-6])

for line in lines:
  data=[]
  old_area=0.

  try:

    left=max(0,int(line[14]-line[3]-5))
    right=min(int(line[14]+line[3]+5),nx)
    bottom=max(0,int(line[15]-line[3]-5))
    top=min(int(line[15]+line[3]+5),ny)

    sum=0.
    npts=0.
    tot_npts=0.
 
    for x in numarray.arange(left,right,1):
      for y in numarray.arange(bottom,top,1):
        eps=1.-line[12] ; a=line[3] ; d=-line[13]*pi/180. ; xc=line[14] ; yc=line[15]
        if x-xc == 0:
          t=pi/2.
        else:
          t=atan((y-yc)/(x-xc))
        if ((x-xc)**2+(y-yc)**2)**0.5 > findr(t,eps,a-rr/2.,d,xc,yc) and \
           ((x-xc)**2+(y-yc)**2)**0.5 < findr(t,eps,a+rr/2.,d,xc,yc):
           print x,y,pix[y-1][x-1]

  except:
    raise
