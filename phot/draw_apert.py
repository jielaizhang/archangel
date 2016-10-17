#!/usr/bin/env python

# quick routine to look at elliptical apertures
# note that python array coords and IRAF coords are off
# by one pixel x/y and flipped; e.g. data(i,j) == pix[j-1][i-1]

import sys, os
from math import *
from ppgplot import *
try:
  import numpy.numarray as numarray
except:
  import numarray
import pyfits
from xml_archangel import *

def ellipse(axis,x,r,s,xc,yc,th):

# routine to solve coeffients of elliptical equation
# of form Ax^2 + By^2 + Cx + Dy + Exy + F = 0

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
      return 'NaN','NaN'
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
      return 'NaN','NaN'

def gray(pix,i1,i2,j1,j2,r1,r2):
  pgeras()
  pgswin(i1,i2,j1,j2)
#  pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2) # note offset to match IRAF coords
  pggray_s(pix[j1:j2,i1:i2],r1,r2,i1,j1,i2,j2) # note offset to match IRAF coords
  pgswin(i1+0.5,i2+0.5,j1+0.5,j2+0.5) # offset 0.5 to match pixel center
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  return

def piece(vert):
  det=0.
  for i in range(len(vert)):
    j=i+1
    if j >= len(vert): j=0
    det=det+(vert[i][0]*vert[j][1]-vert[j][0]*vert[i][1])
  return abs(det/2.)

def edraw(eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  th=0.
  step=2.
  istep=int(360./step)+1
  for i in range(istep):
    th=th+step
    t=th*pi/180.
    c1=bsq*(cos(t))**2+asq*(sin(t))**2
    c2=(asq-bsq)*2*sin(t)*cos(t)
    c3=bsq*(sin(t))**2+asq*(cos(t))**2
    c4=asq*bsq
    r=(c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**.5
    if th == step:
      pgmove(r*cos(t)+xc,r*sin(t)+yc)
    else:
      pgdraw(r*cos(t)+xc,r*sin(t)+yc)
  return

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

if sys.argv[1] == '-h':
  print 'elapert'
  print

pgbeg('/xs',1,1)
pgask(0)
pgscr(0,1.,1.,1.)
pgscr(1,0.,0.,0.)
pgscf(2)
pgpap(10.0,1.0)

fitsobj=pyfits.open(sys.argv[-1],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
aspect=1.
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()

if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
  doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)

  try:
    xsky=float(elements['sky'][0][1])
  except:
    print 'sky value not found, setting to zero'
    xsky=0.
  try:
    skysig=float(elements['skysig'][0][1])
  except:
    print 'skysig not found, setting to one'
    skysig=1.

  try:
    scale=float(elements['scale'][0][1])
  except:
    print 'pixel scale value not found, setting to one'
    scale=1.
  try:
    zpt=float(elements['zeropoint'][0][1])
  except:
    print 'zeropoint not found, setting to 25.'
    zpt=25.

  for t in elements['array']:
    if t[0]['name'] == 'prf':
      pts=[]
      for z in t[2]['axis']:
        pts.append(map(float,z[1].split('\n')))
      tmp=numarray.array(pts)
      pts=numarray.swapaxes(tmp,1,0)
      break

for line in pts:

  if line[3] > 10:
    r1=xsky+50.*skysig
  else:
    r1=xsky+1.2*pix[int(line[15]-1)][int(line[14])-1]
  r2=xsky-0.05*(r1-xsky)
  sum=0.
  npts=0.
  if line[3] < 3: continue

  left=int(line[14]-1.5*line[3])
  right=int(line[14]+1.5*line[3]+1)
  bottom=int(line[15]-1.5*line[3])
  top=int(line[15]+1.5*line[3]+1)

  pgsch(0.8)
  pgsci(1)
  gray(pix,left,right,bottom,top,r1,r2)
  pgsci(3)
  edraw(1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])

  for x in numarray.arange(left+0.5,right,1.0):
    y1,y2=ellipse('x',x,line[3],(1.-line[12])*line[3],line[14],line[15],line[13]*pi/180.)
    if y1 == 'NaN' or y2 == 'NaN':
      pass
    else:
      pgpt(numarray.array([x]),numarray.array([y1]),4)
      pgpt(numarray.array([x]),numarray.array([y2]),4)

  for y in numarray.arange(bottom+0.5,top,1.0):
    x1,x2=ellipse('y',y,line[3],(1.-line[12])*line[3],line[14],line[15],line[13]*pi/180.)
    if x1 == 'NaN' or x2 == 'NaN':
      pass
    else:
      pgpt(numarray.array([x1]),numarray.array([y]),4)
      pgpt(numarray.array([x2]),numarray.array([y]),4)

  pgsci(4)
  for x in numarray.arange(left,right,1):
    for y in numarray.arange(bottom,top,1):
      area=0.
      tmp=inside(x,y,1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])
      vert=[]
      if tmp and len(tmp) < 4:
        y1,y2=ellipse('x',x-0.5,line[3],(1.-line[12])*line[3], \
                      line[14],line[15],line[13]*pi/180.)
        if y1 != 'NaN' and y2 != 'NaN':
          if ((y-y1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x-0.5,y1))
          if ((y-y2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x-0.5,y2))
        y1,y2=ellipse('x',x+0.5,line[3],(1.-line[12])*line[3], \
                      line[14],line[15],line[13]*pi/180.)
        if y1 != 'NaN' and y2 != 'NaN':
          if ((y-y1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x+0.5,y1))
          if ((y-y2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x+0.5,y2))
        x1,x2=ellipse('y',y-0.5,line[3],(1.-line[12])*line[3], \
                      line[14],line[15],line[13]*pi/180.)
        if x1 != 'NaN' and x2 != 'NaN':
          if ((x-x1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x1,y-0.5))
          if ((x-x2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x2,y-0.5))
        x1,x2=ellipse('y',y+0.5,line[3],(1.-line[12])*line[3], \
                      line[14],line[15],line[13]*pi/180.)
        if x1 != 'NaN' and x2 != 'NaN':
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
      if area > 0.:
        pgptxt(x,y,0.,0.,'%4.2f' % area)
#      if area > 0: print x,y,area,pix[y-1][x-1],line[14],line[15]
# watch the pixel offset
      sum=sum+area*pix[y-1][x-1]
      npts=npts+area

  print line[3],sum,npts
  test=raw_input()
  if test == '/': break

