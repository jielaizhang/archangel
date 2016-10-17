#!/usr/bin/env python

import pyfits,sys,os
try:
  import numpy.numarray as numarray
except:
  import numarray
from ppgplot import *
from math import *

# quick display program ala prf_edit, enter a list of files or -f image
# output to a GIF file

def eplot(prf,i1,i2,j1,j2):
  pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
  for line in prf:
    if line[6] == 0:
      pgsci(2)
    elif line[6] == -1:
      pgsci(3)
    else:
      pgsci(4)
    edraw(1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])
  pgsci(1)
  return

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

def gray(pix,i1,i2,j1,j2,r1,r2):
  pgpap(10.,aspect)
  pgswin(i1,i2,j1,j2)
  pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
  pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  pgptxt((i2-i1)/2.+i1+1.5,0.05*(j2-j1)+(j2+1.5),0.,0.5,filename+' '+prf_op)
  tmp='%6.1f' % r2
  pgptxt(i1+1.5,(j1+1.5)-0.10*(j2-j1),0.,0.5,tmp)
  tmp='%6.1f' % r1
  pgptxt(i2+1.5,(j1+1.5)-0.10*(j2-j1),0.,0.5,tmp)
  return

# main

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: display.py option master_file'
  print ''
  print '       -f = do this image only'
  print '       -p = do this image plus ellipses'
  print '       -m = do file of images'
  sys.exit()

pgbeg('junk.gif/gif',1,1)
pgask(0)
pgscr(0,1.,1.,1.)
pgscr(1,0.,0.,0.)
pgscf(2)
pgsch(1.0)

filename=sys.argv[-1]
prf_op=''

if not os.path.isfile(filename):
  print filename,'not found -- ABORTING'
  sys.exit(0)
fitsobj=pyfits.open(filename,"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
aspect=float(ny)/nx
hdr=fitsobj[0].header
#print hdr.items()
pix=fitsobj[0].data
fitsobj.close()

try:
  file=open(filename.split('.')[0]+'.sky','r')
  line=file.readline()
  if not line:
    file.close()
    raise
  xsky=line.split()[0]
  skysig=line.split()[1]
except:
  cmd='sky_box -f '+filename
  sky=os.popen(cmd).read()
  if len(sky) < 1:
    print 'file not found?'
    sys.exit()
  xsky=sky.split()[2]
  skysig=sky.split()[3]

try:
  r1=float(xsky)+50.*float(skysig)
  r2=float(xsky)-0.05*(r1-float(xsky))
except:
  r1=100.
  r2=float(xsky)-10.

gray(pix,1,nx,1,ny,r1,r2)

if sys.argv[1] == '-p':
  file=open(filename.split('.')[0]+'.prf','r')
  prf=[]
  while 1:
    line=file.readline()
    if not line: break
    tmp=[]
    for x in line.split(): tmp.append(float(x))
    if tmp[13] >= 270: tmp[13]=tmp[13]-360.
    if tmp[13] > 90: tmp[13]=tmp[13]-180.
    if tmp[13] <= -270: tmp[13]=tmp[13]+360.
    if tmp[13] < -90: tmp[13]=tmp[13]+180.
    prf.append(tmp)
  file.close()
  eplot(prf,1,nx,1,ny)

x=[] ; y=[]
if max(nx,ny) < 400:
#  n=0
#  for tmp in pix.flat:
#    if str(tmp) == 'nan':
#      n+=1
  for j in xrange(ny):
    for i in xrange(nx):
      if str(pix[j,i]) == 'nan':
        x.append(i+1.0)
        y.append(j+1.0)
xs=numarray.array(x)
ys=numarray.array(y)
pgswin(2,nx+1.0,2,ny+1.5)
pgsci(2)
pgpt(xs,ys,-2)
pgsci(1)
pgend()
