#!/usr/bin/env python

import sys, numarray, math, os
from ppgplot import *
import pyfits
from matfunc import *

def do_fit(x,lum):
  fit=numarray.array([x,lum])
  a,b,c=polyfit(fit,2)
  z=[]
  err=0.
  for t1,t2 in zip(x,lum):
    z.append(a*t1**2+b*t1+c)
    err=err+(t2-(a*t1**2+b*t1+c))**2
  return z,a,b,c,(err/len(x))**0.5

fitsobj=pyfits.open(sys.argv[1],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
pix=fitsobj[0].data

tmp=os.popen('sky_box -t '+sys.argv[-1]).read()
sky=float(tmp.split()[2])
skysig=float(tmp.split()[3])

x=[]
raw=[]
xlow=1.e33
xhi=-1.e33
for line in pix:
  for dot in line:
    if dot > sky-5.*skysig and dot < sky+5.*skysig:
      x.append(dot)
      if dot < xlow: xlow=dot
      if dot > xhi: xhi=dot
raw.append(x)

pgbeg('/xs')
pgscr(0,1.,1.,1.)
pgscr(1,0.,0.,0.)
pgscf(2)
pgsch(1.2)

nbin=int(xhi-xlow)
xbin=1.
data=[]
bin=[]
for i in range(nbin+1):
  bin.append(i*xbin-xbin/2.+xlow)
  data.append(0)
for s in x:
  for w in range(len(bin)-1):
    if s >= bin[w] and s < bin[w+1]:
      data[w]=data[w]+1
ylow=0.
yhi=0.
for w in data:
  if w > yhi: yhi=w+0.1*w

pgswin(xlow,xhi,ylow,yhi)
pgbox('bcnst',0.,0,'bcnst',0.,0)
pglab('','N','')
#pgbin_s(numarray.array(data),xlow,xhi)
pgpt(numarray.array(bin),numarray.array(data),5)

line=''
title=''
xlab=''
norm=0
ifit=0
while 1:
  d=pgband(0)
  if d[2] == '/': break

  elif d[2] == 'f':
    ifit+=1
    if norm:
      zz,a,b,c,err1=do_fit(step_store[ifit:-ifit],xstore[ifit:-ifit])
    else:
      zz,a,b,c,err1=do_fit(bin[ifit:-ifit],data[ifit:-ifit])
    x0=-b/(2.*a)
    print a,b,c,-b/(2.*a),a*x0**2+b*x0+c

  elif d[2] == 'n': norm=abs(norm-1)

  pgeras()
  pgswin(xlow,xhi,ylow,yhi)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  pglab(xlab,'N',title)
  pgpt(numarray.array(bin),numarray.array(data),5)
  if norm:
    xbin=1.
    xstep=1.
    step=xlow
    last=0.
    for tmp in numarray.arange(xlow,xhi,1.):
      step=step+xstep
      xsum=0.
      for m in range(len(x)):
        z=(step-x[m])/(xbin/2.)
        xsum=xsum+math.exp(-0.5*z**2)
      if xsum < last: break
      print step,xsum
      last=xsum
    print '1st',last,step,xsum
    step=step-2.*xstep
    xstep=0.1
    step=step-xstep
    last=0.
    for tmp in numarray.arange(21):
      step=step+xstep
      xsum=0.
      for m in range(len(x)):
        z=(step-x[m])/(xbin/2.)
        xsum=xsum+math.exp(-0.5*z**2)
      if xsum < last: break
      print step,xsum
      last=xsum
    print '2nd',last,step,xsum
    sys.exit()

    yhi=0.
    xstore=[]
    step_store=[]
    for x in raw:
#      xstep=(xhi-xlow)/100
      xstep=1.
      step=xlow
      for tmp in numarray.arange(xlow,xhi,1.):
        xsum=0.
        for m in range(len(x)):
          z=(step-x[m])/(xbin/2.)
          xsum=xsum+math.exp(-0.5*z**2)
        if xsum > yhi: yhi=xsum
        step_store.append(step)
        xstore.append(xsum)
        step=step+xstep
    yhi=yhi+0.1*yhi
    pgswin(xlow,xhi,ylow,yhi)
    pgmove(step_store[0],xstore[0])
    for z1,z2 in zip(step_store,xstore):
      pgdraw(z1,z2)
    pgpt(numarray.array(step_store),numarray.array(xstore),3)

  pgsci(1)

  try:
    pgsci(2)
    pgline(numarray.array(bin[ifit:-ifit]),numarray.array(zz))
    pgsci(1)
  except:
    pass
