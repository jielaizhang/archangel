#!/usr/bin/env python

import sys, numarray, math
from ppgplot import *

def xits(x,xsig):
  xmean1=0. ; sig1=0.
  for tmp in x:
    xmean1=xmean1+tmp
  try:
    xmean1=xmean1/len(x)
  except:
    return 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'
  for tmp in x:
    sig1=sig1+(tmp-xmean1)**2
  try:
    sig1=(sig1/(len(x)-1))**0.5
  except:
    return 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'
  xmean2=xmean1 ; sig2=sig1
  xold=xmean2+0.001*sig2
  its=0
  while (xold != xmean2 and its < 100):
    xold=xmean2
    its+=1
    dum=0.
    npts=0
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        npts+=1
        dum=dum+tmp
    try:
      xmean2=dum/npts
    except:
      return xmean1,sig1,'NaN','NaN',len(x),'NaN','NaN'
    dum=0.
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        dum=dum+(tmp-xmean2)**2
    try:
      sig2=(dum/(npts-1))**0.5
    except:
      return xmean1,sig1,'NaN','NaN',len(x),'NaN','NaN'
  return xmean1,sig1,xmean2,sig2,len(x),npts,its

def draw():
  nbin=int((xhi-xlow)/xbin)
  rdata=[]
  yhi=0.
  for x in raw:
    bin=[]
    data=[]
    for i in range(nbin+1):
      bin.append(i*xbin-xbin/2.+xlow)
      data.append(0)
    for s in x:
      for w in range(len(bin)-1):
        if s >= bin[w] and s < bin[w+1]:
          data[w]=data[w]+1
    rdata.append(data)
    for w in data:
      if w > yhi: yhi=w
  yhi=yhi+0.1*yhi
  pgeras()
  pgswin(xlow,xhi,ylow,yhi)
  icolor=0
  if norm:
    yhi=0.
    for x in raw:
      xstep=(xhi-xlow)/100
      step=xlow
      for tmp in range(100):
        xsum=0.
        for m in range(len(x)):
          z=(step-x[m])/(xbin/2.)
          xsum=xsum+math.exp(-0.5*z**2)
        if xsum > yhi: yhi=xsum
        step=step+xstep
    yhi=yhi+0.1*yhi
    pgswin(xlow,xhi,ylow,yhi)
    for x in raw:
      icolor=icolor+1
      pgsci(icolor)
      xstep=(xhi-xlow)/100
      step=xlow
      pgmove(xlow,0.)
      for tmp in range(100):
        xsum=0.
        for m in range(len(x)):
          z=(step-x[m])/(xbin/2.)
          xsum=xsum+math.exp(-0.5*z**2)
        pgdraw(step,xsum)
        step=step+xstep
  else:
    for data in rdata:
      icolor=icolor+1
      pgsci(icolor)
      adata=numarray.array(data)
      pgbin_s(adata,xlow,xhi)
  pgsci(1)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  pglab(xlab,'N',title)
  try:
    pgsci(4)
    pgptxt(xlow,yhi+0.05*(yhi-ylow),0.,0.,'%6.3g' % a[2])
    pgpt(numarray.array([a[2]]),numarray.array([yhi-0.05*(yhi-ylow)]),31)
    pgsci(1)
  except:
    pass

if sys.argv[1] == '-h':
  print 'Usage: hist data_file column_number'
  print
  print 'options:  lower, upper, bin size'
  print '          f = new file'
  print '          n = normalized histogram'
  print '          h = hardcopy (junk.ps)'
  print '          m = output histogram to mongo file'
  print '          t = enter title'
  print '          x = enter xlab'
  print '          q = exit'
  sys.exit()

try:
  col=int(sys.argv[2])
except:
  col=0

file=open(sys.argv[1],'r')
x=[]
raw=[]
xlow=1.e33
xhi=-1.e33
while 1:
  line=file.readline()
  if not line or line == '\n': break
  x.append(float(line.split()[col]))
  if float(line.split()[col]) < xlow: xlow=float(line.split()[col])
  if float(line.split()[col]) > xhi: xhi=float(line.split()[col])
file.close()
raw.append(x)
a=xits(x,3.0)

pgbeg('/xs')
pgscr(0,1.,1.,1.)
pgscr(1,0.,0.,0.)
pgscf(2)
pgsch(1.2)

nbin=20
xbin=(xhi-xlow)/nbin
data=[]
bin=[]
for i in range(nbin+1):
  bin.append(i*xbin-xbin/2.+xlow)
  data.append(0)
for s in x:
  for w in range(len(bin)-1):
    if s >= bin[w] and s < bin[w+1]:
      data[w]=data[w]+1
adata=numarray.array(data)
ylow=0.
yhi=0.
for w in data:
  if w > yhi: yhi=w+0.1*w

#pgswin(xlow,xhi,ylow,yhi)
#pgbox('bcnst',0.,0,'bcnst',0.,0)
#pglab('','N','')
#pgbin_s(adata,xlow,xhi)

line=''
title=''
xlab=''
norm=0
draw()

while 1:

  d=pgband(0)
  if d[2] == '/': break

  if d[2] == '?':
    print 'Usage: hist data_file column_number'
    print
    print 'options:  lower, upper, bin size'
    print '          f = new file'
    print '          n = normalized histogram'
    print '          h = hardcopy (junk.ps)'
    print '          m = output histogram to mongo file'
    print '          t = enter title'
    print '          x = enter xlab'
    print '          q = exit'

  elif d[2] == 'f':
    line='Enter new file name: '
    pgswin(0.,1.,0.,1.)
    pgptxt(0.,-.1,0.,0.,line)
    file=''
    while 1:
      d=pgband(0)
      if d[2] == '\r':
        break
      else:
        pgsci(0)
        pgptxt(0.,-.1,0.,0.,line+file)
        if d[2] == '\b':
          file=file[:-1]
        else:
          file=file+d[2]
          pgswin(0.,1.,0.,1.)
          pgsci(1)
          pgptxt(0.,-.1,0.,0.,line)
        pgsci(1)
        pgptxt(0.,-.1,0.,0.,line+file)
    input=open(file,'r')
    x=[]
    while 1:
      line=input.readline()
      if not line or line == '\n': break
      x.append(float(line.split()[col]))
    input.close()
    raw.append(x)

  elif d[2] == 'n': norm=abs(norm-1)

  elif d[2] == 't':
    while 1:
      d=pgband(0)
      if d[2] == '\r':
        break
      else:
        pgsci(0)
        pglab(xlab,'N',title)
        if d[2] == '\b':
          title=title[:-1]
        else:
          title=title+d[2]
        pgsci(1)
      pglab(xlab,'N',title)

  elif d[2] == 'x':
    while 1:
      d=pgband(0)
      if d[2] == '\r':
        break
      else:
        pgsci(0)
        pglab(xlab,'N',title)
        if d[2] == '\b':
          lxlab=xlab[:-1]
        else:
          xlab=xlab+d[2]
        pgsci(1)
      pglab(xlab,'N',title)

  elif d[2] == 'h':
    pgend()
    pgbeg('junk.ps/cps')
    pgscr(0,1.,1.,1.)
    pgscr(1,0.,0.,0.)
    pgscf(2)
    pgsch(1.2)
    print 'hardcopy to junk.ps'
    draw()
    pgbeg('/xs')
    pgscr(0,1.,1.,1.)
    pgscr(1,0.,0.,0.)
    pgscf(2)
    pgsch(1.2)

  elif d[2] == 'm':
    line='Enter mongo file name: '
    pgswin(0.,1.,0.,1.)
    pgptxt(0.,-.1,0.,0.,line)
    file=''
    nbin=int((xhi-xlow)/xbin)
    rdata=[]
    for x in raw:
      bin=[]
      data=[]
      for i in range(nbin+1):
        bin.append(i*xbin-xbin/2.+xlow)
        data.append(0)
      for s in x:
        for w in range(len(bin)-1):
          if s >= bin[w] and s < bin[w+1]:
            data[w]=data[w]+1
      rdata.append(data)
    while 1:
      d=pgband(0)
      if d[2] == '\r':
        out=open(file,'w')
        icolor=0
        if norm:
          for x in raw:
            icolor=icolor+1
            xstep=(xhi-xlow)/100
            step=xlow
            pgmove(xlow,0.)
            out.write(str(xlow)+' '+str(0.)+' '+str(icolor)+'\n')
            for tmp in range(100):
              xsum=0.
              for m in range(len(x)):
                z=(step-x[m])/(xbin/2.)
                xsum=xsum+math.exp(-0.5*z**2)
              out.write(str(step)+' '+str(xsum)+' '+str(icolor)+'\n')
              step=step+xstep
        else:
          for data in rdata:
            icolor=icolor+1
            for i in range(len(bin)):
              out.write(str(bin[i])+' '+str(data[i])+' '+str(icolor)+'\n')
        out.close
        break

      else:
        pgsci(0)
        pgptxt(0.,-.1,0.,0.,line+file)
        if d[2] == '\b':
          file=file[:-1]
        else:
          file=file+d[2]
          pgswin(0.,1.,0.,1.)
          pgsci(1)
          pgptxt(0.,-.1,0.,0.,line)
        pgsci(1)
        pgptxt(0.,-.1,0.,0.,line+file)

  else:
    pgswin(0.,1.,0.,1.)
    line=d[2]
    pgptxt(0.,-.1,0.,0.,line)
    while 1:
      d=pgband(0)
      if d[2] == '\r':
        if len(line.split()) == 3:
          xlow=float(line.split()[0])
          xhi=float(line.split()[1])
          xbin=float(line.split()[2])
          nbin=int((xhi-xlow)/xbin)
          break
      pgsci(0)
      pgptxt(0.,-.1,0.,0.,line)
      if d[2] == '\b':
        line=line[:-1]
      else:
        line=line+d[2]
      if len(line) == 0: break
      pgsci(1)
      pgptxt(0.,-.1,0.,0.,line)
    tmp=[]
    for t in x:
      if t > xlow and t <= xhi: tmp.append(t)
    a=xits(tmp,3.0)

  draw()
