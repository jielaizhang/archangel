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

def ellipse(axis,x,r,s,xc,yc,th):

# routine to solve coeffients of elliptical equation
# of form Ax^2 + By^2 + Cx + Dy + Exy + F = 0
# r = major axis, s = minor axis

  m=cos(th)
  n=sin(th)
  xo=0.
  yo=0.
  a=(s**2)*(m**2)+(r**2)*(n**2)
  b=(s**2)*(n**2)+(r**2)*(m**2)
  c=-2.*((s**2)*m*xo+(r**2)*n*yo)
  d=-2.*((s**2)*n*xo+(r**2)*m*yo)
  e=2.*((s**2)*m*n-(r**2)*m*n)
  f=(s**2)*(xo**2)+(r**2)*(yo**2)-(r**2)*(s**2)

# for given x value, find two y values on ellipse
  if axis == 'x':
    x=x-xc
    t1=(d+e*x)
    t2=t1**2
    t3=4.*b*(a*(x**2)+c*x+f)
    t4=2.*b
    try:
      return yc+(-t1+(t2-t3)**0.5)/t4,yc+(-t1-(t2-t3)**0.5)/t4
    except:
      return 'nan','nan'
# for given y value, find two x values on ellipse
  else:
    x=x-yc
    t1=(c+e*x)
    t2=t1**2
    t3=4.*a*(b*(x**2)+d*x+f)
    t4=2.*a
    try:
      return xc+(-t1+(t2-t3)**0.5)/t4,xc+(-t1-(t2-t3)**0.5)/t4
    except:
      return 'nan','nan'

def piece(vert):
  det=0.
  for i in range(len(vert)):
    j=i+1
    if j >= len(vert): j=0
    det=det+(vert[i][0]*vert[j][1]-vert[j][0]*vert[i][1])
  return abs(det/2.)

def findr(t,eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  c1=bsq*(cos(t))**2+asq*(sin(t))**2
  c2=(asq-bsq)*2*sin(t)*cos(t)
  c3=bsq*(sin(t))**2+asq*(cos(t))**2
  c4=asq*bsq
  return (c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**0.5

def inside(x,y,eps,a,d,xc,yc):
  edge=[]
  for i in [x-0.5,x+0.5]:
    for j in [y-0.5,y+0.5]:
      if i-xc == 0:
        t=pi/2.
      else:
        t=atan((j-yc)/(i-xc))
      if ((i-xc)**2+(j-yc)**2)**0.5 < findr(t,eps,a,d,xc,yc):
        edge.append((i,j))
  return edge

# main

if sys.argv[1] == '-h':
  print 'aperture options fits_file xc yc a b theta'
  print ' or'
  print 'aperture options fits_file xc yc major_axis eps=(1-b/a) theta'
  print
  print 'options:   -h = this message'
  print '         -sky = new sky value'
  print '           -m = print pixels used (marks)'
  print '           -g = use gasp_images output (s.tmp)'
  sys.exit()

if '-g' in sys.argv:
  ifile=-1
else:
  ifile=-6

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
        area=0.
        tmp=inside(x,y,1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])
        vert=[]
        if tmp and len(tmp) < 4:
          y1,y2=ellipse('x',x-0.5,line[3],(1.-line[12])*line[3], \
                        line[14],line[15],line[13]*pi/180.)
          if str(y1) != 'nan' and str(y2) != 'nan':
            if ((y-y1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x-0.5,y1))
            if ((y-y2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x-0.5,y2))
          y1,y2=ellipse('x',x+0.5,line[3],(1.-line[12])*line[3], \
                        line[14],line[15],line[13]*pi/180.)
          if str(y1) != 'nan' and str(y2) != 'nan':
            if ((y-y1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x+0.5,y1))
            if ((y-y2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x+0.5,y2))
          x1,x2=ellipse('y',y-0.5,line[3],(1.-line[12])*line[3], \
                        line[14],line[15],line[13]*pi/180.)
          if str(x1) != 'nan' and str(x2) != 'nan':
            if ((x-x1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x1,y-0.5))
            if ((x-x2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x2,y-0.5))
          x1,x2=ellipse('y',y+0.5,line[3],(1.-line[12])*line[3], \
                        line[14],line[15],line[13]*pi/180.)
          if str(x1) != 'nan' and str(x2) != 'nan':
            if ((x-x1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x1,y+0.5))
            if ((x-x2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x2,y+0.5))

          if vert:
            x0=vert[-1][0]
            y0=vert[-1][1]
            for i in range(len(tmp)):
              dmin=1.e33
              for r,s in tmp:
                dd=((x0-r)**2+(y0-s)**2)**0.5
                if dd < dmin:
                  t=(r,s)
                  dmin=dd
              try:
                x0=t[0]
                y0=t[1]
                vert.append(t)
                tmp.remove(t)
              except:
                pass
            area=piece(vert)
        elif len(tmp) == 4:
          area=1.
        if '-m' in sys.argv and area > 0: print x,y,area,pix[y-1][x-1],pix[y-1][x-1]-xsky,line[14],line[15]
# watch the pixel offset
        if str(pix[y-1][x-1]) != 'nan':
#          print sum,pix[y-1][x-1]
          sum=sum+area*(pix[y-1][x-1]-xsky)
          npts=npts+area
        tot_npts=tot_npts+area

    if '-m' not in sys.argv:
      try:
        -2.5*log10(sum)
        print '%16.8e' % line[3],
        print '%16.8e' % (-2.5*log10(sum)),
        print '%16.8e' % (-2.5*log10(sum)+zpt),
        print '%16.8e' % sum,
        print '%16.8e' % npts
      except:
        print '%16.8e' % line[3],
        print 'nan',
        print 'nan',
        print '%16.8e' % sum,
        print '%16.8e' % npts
    old_int=line[0]
    old_area=tot_npts

  except:
    raise
