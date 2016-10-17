#!/usr/bin/env python

import sys,os
import astropy.io.fits as pyfits
from math import *

if '-h' in sys.argv:
  print 'thres_prf data_file xc yc'
  print
  print 'takes data_file and does moment fits out to nx/4'
  print
  print 'if xc and yc used, holds fit to those coords'
  print
  print 'options: -f = use file of thresholds'
  sys.exit()

for z in sys.argv[1:]:
  if '.' in z:
    file=z
    break

sky=float(os.popen('xml_archangel -o '+file.split('.')[0]+' sky').read())
sig=float(os.popen('xml_archangel -o '+file.split('.')[0]+' skysig').read())

fitsobj=pyfits.open(file,"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
hdr=fitsobj[0].header
pix=fitsobj[0].data

try:
  x0=float(sys.argv[-2])
  y0=float(sys.argv[-1])
  rmin=20.
except:
  x0=nx/2.
  y0=ny/2.
  rmin=nx/4.

#xsig=pix[int(y0)-1][int(x0)-1]/3.
#xsig=9000.
xsig=50.
#xsig=0.5

if '-f' in sys.argv:
  thres=[tmp[:-1] for tmp in open(sys.argv[-1],'r').readlines()]
else:
  thres=range(100)

for i in thres:
  if '-f' in sys.argv:
#    print 'gasp_images -f '+file+' '+str(sky)+' '+str(i)+' 10 false'
    tmp=os.popen('gasp_images -f '+file+' '+str(sky)+' '+str(i)+' 10 false').read()
#    print tmp
  else:
#  print xsig,0.25*xsig,xsig-0.25*xsig,sig*(xsig-0.25*xsig)
    xsig=xsig-0.25*xsig
#  xsig=xsig+(i/4.)
    if xsig < 0.01: break
    if xsig > 3.:
      size=10
    else:
      size=xsig*(100.-10.)/(0.5-3.)+118.
#  print 'gasp_images -f '+file+' '+str(sky)+' '+str(xsig*sig)+' '+str(int(size))+' false',xsig/sig
    tmp=os.popen('gasp_images -f '+file+' '+str(sky)+' '+str(xsig*sig)+' '+str(int(size))+' false').read()

  xmin=-1.e33
  rmin=nx/4.
  for ell in tmp.split('\n'):
    if len(ell) == 0: break
    r=((float(ell.split()[0])-x0)**2+(float(ell.split()[1])-y0)**2)**0.5
    try:
      xfact=float(ell.split()[2])/r
    except ZeroDivisionError:
      xfact=float(ell.split()[2])
    if xfact > xmin and r < rmin:
      xmin=xfact
      hold=ell
#  if xmin == -1.e33: break
  if xmin != -1.e33:
    x0=float(hold.split()[0])
    y0=float(hold.split()[1])
    eps=1.-float(hold.split()[3])
    a=(float(hold.split()[2])/(eps*pi))**0.5
    dd=float(hold.split()[4])
    xc=float(hold.split()[0])
    yc=float(hold.split()[1])
    print xsig*sig,'0. 0.',a,'0. 0. 1. 0. 0. 0. 0. 0.',1.-eps,dd,xc,yc,'0. 0.'
    rmin=max(10.,(float(hold.split()[2])/pi)**0.5)
