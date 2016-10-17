#!/usr/bin/env python

import sys,os
import astropy.io.fits as pyfits
try:
  import numpy.numarray as numarray
except:
  import numarray
from ppgplot import *
from math import *

# make a mess of gif files, then processed into thumbnails and html file

def gray_th(pix,i1,i2,j1,j2,r1,r2):
  pgpap(1.,aspect)
  pgswin(i1,i2,j1,j2)
  pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
  return

def gray(pix,i1,i2,j1,j2,r1,r2):
  pgpap(10.,aspect)
  pgswin(i1,i2,j1,j2)
  pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
  pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  pgptxt((i2-i1)/2.+i1+1.5,0.05*(j2-j1)+(j2+1.5),0.,0.5,filename)
  return

# main

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: thumbnail op master_file'
  print '       -f = make gifs and output html'
  sys.exit()

print '<html><table>'
n=-1

master=open(sys.argv[-1],'r')
while 1:

  filename=master.readline()[:-1]
  if not filename: break

  if sys.argv[1] == '-f':
    fitsobj=pyfits.open(filename,"readonly")
    nx=fitsobj[0].header['NAXIS1']
    ny=fitsobj[0].header['NAXIS2']
    aspect=float(ny)/nx
    hdr=fitsobj[0].header
    pix=fitsobj[0].data
    fitsobj.close()
    clean=0

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

    pgbeg(filename.replace('fits','gif')+'/gif',1,1)
    pgask(0)
    pgscr(0,1.,1.,1.)
    pgscr(1,0.,0.,0.)
    pgscf(2)
    pgsch(1.0)
    gray(pix,1,nx,1,ny,r1,r2)
    pgend()

    pgbeg(filename.replace('.fits','_th.gif')+'/gif',1,1)
    pgask(0)
    pgscr(0,1.,1.,1.)
    pgscr(1,0.,0.,0.)
    pgscf(2)
    pgsch(1.0)
    gray_th(pix,1,nx,1,ny,r1,r2)
    pgend()

  n+=1
  if n == 8:
    n=0
    print '</td></tr><tr><td>'
  else:
    print '</td><td>'
  print '<center><a href="'+filename.replace('fits','gif')+ \
        '"><img src="'+filename.replace('.fits','_th.gif')+'"></a><br>'+ \
        filename.replace('_j.fits','').upper()+'</center>'

print '</table>'
