#!/usr/bin/env python

import pyfits,sys,os
try:
  import numpy.numarray as numarray
except:
  import numarray
from ppgplot import *
from math import *

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'qphot filename r1 r2'
  print
  print 'Cursor options: c = contrast control'
  print '                z = zoom'
  print '                r = reset'
  print '                s = scan, 1st at 5 sigma, sigma control for later'
  print '                p = print pixels around cursor'
  sys.exit()

file=open(sys.argv[1].split('.')[0]+'.sky','r')
line=file.readline()
sky=float(line.split()[0])
sig=float(line.split()[1])
file.close()

fitsobj=pyfits.open(sys.argv[1],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
hdr=fitsobj[0].header
#print hdr.items()
pix=fitsobj[0].data

if len(sys.argv) > 2:
  r2=float(sys.argv[2])
  r1=float(sys.argv[3])
else:
  r1=sky+50.*sig
  r2=sky-0.05*(r1-sky)

pgbeg('/xs')
pgscr(0,1.,1.,1.)
pgscr(1,0.,0.,0.)
pgscf(2)
aspect=float(ny)/float(nx)
pgpap(0.,aspect)
pgswin(2.,nx+1.0,2.,ny+1.0)
i1=1
i2=nx
j1=1
j2=ny
pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
pgswin(1.+1.5,nx+1.5,1.+1.5,ny+1.5)
pgbox('bcnst',0.,0,'bcnst',0.,0)

xsig=0.
x0=nx/2.
y0=ny/2.
xstep=nx/2.

while 1:
  d=pgband(0)

  if d[2] == 'q': break

  if d[2] == 'r':
    xsig=0.
    xstep=nx/2
    i1=1
    i2=nx
    j1=1
    j2=ny
    pgeras()
    pgswin(i1,i2,j1,j2)
    pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
    pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
    pgbox('bcnst',0.,0,'bcnst',0.,0)

  if d[2] == 'z':
    if xstep > 4.: xstep=int(xstep/2)+1
    i1=int(round(d[0]-xstep))-1
    i2=int(round(d[0]+xstep))-2
    if i1 < 1:
      i1=1
      i2=int(2*xstep+i1)
    if i2 > nx:
      i1=int(nx-2*xstep)
      i2=nx
    j1=int(round(d[1]-xstep))-1
    j2=int(round(d[1]+xstep))-2
    if j1 < 1:
      j1=1
      j2=int(2*xstep+j1)
    if j2 > ny:
      j1=int(ny-2*xstep)
      j2=ny
    pgeras()
    pgswin(i1,i2,j1,j2)
    pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
    pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
    pgbox('bcnst',0.,0,'bcnst',0.,0)

  if d[2] == 'p':
    x=int(round(d[0]))-1
    y=int(round(d[1]))-1
    print '\n',' '
    for i in range(x-2,x+3): print '%8.0i' % (i+1),
    for j in range(y+2,y-3,-1):
      print '\n',(j+1),
      for i in range(x-2,x+3):
        print '%8.2f' % pix[j][i],

  if d[2] == 'c':
    rold=r1
    k=d[0]*1.5/(i2-i1)+0.5-1.5*i1/(i2-i1)
    r1=r1*k
    if r1 < sky: r1=(rold-sky)/2.+sky
    r2=sky-0.05*(r1-sky)
    pgeras()
    pgswin(i1,i2,j1,j2)
    pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
    pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
    pgbox('bcnst',0.,0,'bcnst',0.,0)

  if d[2] == 's':
    if xsig == 0:
      x0=float(d[0])
      y0=float(d[1])
      xsig=5.
    else:
      mid=j1+(j2-j1)/2.
      xsig=xsig+2.*(mid-float(d[1]))/(j2-j1)
    pgeras()
    pgswin(i1,i2,j1,j2)
    pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
    pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
    pgbox('bcnst',0.,0,'bcnst',0.,0)
    tmp=os.popen('gasp_images -f '+sys.argv[1]+' '+str(sky)+' '+str(xsig*sig)+' 2 false').read()
    pgsci(4)
    rmin=1.e33
    for ell in tmp.split('\n'):
      if len(ell) == 0: break
      r=((float(ell.split()[0])-x0)**2+(float(ell.split()[1])-y0)**2)**0.5
      if r < rmin: rmin=r
    for ell in tmp.split('\n'):
      if len(ell) == 0: break
      r=((float(ell.split()[0])-x0)**2+(float(ell.split()[1])-y0)**2)**0.5
      if r == rmin:
        eps=1.-float(ell.split()[3])
        if eps == 0: eps=0.99
        a=(float(ell.split()[2])/(eps*pi))**0.5
        dd=(-float(ell.split()[4]))*pi/180.
        xc=float(ell.split()[0])
        yc=float(ell.split()[1])
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
          r=(c4/(c1*(cos(dd))**2+c2*sin(dd)*cos(dd)+c3*(sin(dd))**2))**.5
          if th == step:
            pgmove(r*cos(t)+xc,r*sin(t)+yc)
          else:
            pgdraw(r*cos(t)+xc,r*sin(t)+yc)
        break
    pgsci(1)
    strng=ell[:-10]+' \gs = '+'%4.1f' % xsig
    pgptxt(i1+(i2-i1)/2.,j2+0.05*(j2-j1),0.,0.5,strng)
    pgsci(1)
