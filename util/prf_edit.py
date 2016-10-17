#!/usr/bin/env python

import pyfits,sys,os
import numarray
from ppgplot import *
from math import *

def plot(prf,i1,i2,xmin,xmax,ymin,ymax,sky,ierase):
  pgpanl(1,1)
  if ierase == 0: pgeras()
  pgvsiz(0.5,6.5,2.7,4.1)
  ymax=-1.e33
  ymin=+1.e33
  for line in prf:
    y=line[0]-sky
    if line[3] < (i2-i1)/2. and y > 0:
      xmax=line[3]
      if -2.5*log10(y) > ymax: ymax=-2.5*log10(y)
      if -2.5*log10(y) < ymin: ymin=-2.5*log10(y)
  ymax=ymax+0.1*abs(ymax-ymin)
  ymin=ymin-0.1*abs(ymax-ymin)
  xmin=prf[1][3]-0.05*(xmax-prf[1][3])
  xmax=xmax+0.1*xmax
  pgswin(xmin,xmax,ymax,ymin)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  for line in prf:
    if line[6] == 0:
      pgsci(2)
    elif line[6] == -1:
      pgsci(3)
    else:
      pgsci(4)
    try:
      y=line[0]-sky
      xs=numarray.array([line[3]])
      ys=numarray.array([-2.5*log10(y)])
      if y > 0: pgpt(xs,ys,5)
    except:
      pass
  pgsci(1)
  return

def edraw(eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  th=0.
  if eps < 0.2:
    step=0.5
  else:
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
  rr=(c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**.5
  return rr

def gray(pix,i1,i2,j1,j2,r1,r2):
  pgpanl(1,2)
  pgeras()
  pgvsiz(0.5,6.5,0.5,6.5)
  pgswin(i1,i2,j1,j2)
  pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
  pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  return

def eplot(prf,i1,i2,j1,j2):
  pgpanl(1,2)
  pgvsiz(0.5,6.5,0.5,6.5)
  pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
#  x=(i1+1.5)+1.6*(i2-i1)
#  dy=(j2-j1)/30.
#  y=j2+1.5
  pgscf(1)
  y=1.00
  dy=0.035
  pgmtxt('RV',1.,1.05,0.,'_'*(20-len(filename))+filename+'_'*(30-len(filename)))
  pgmtxt('RV',1.,y,0.,'   Inten   Rad  b/a    P.A.    XC     YC')
#  pgptxt(x,y+2.*dy,0.,1.,'_'*(20-len(filename))+filename+'_'*(30-len(filename)))
#  pgptxt(x,y,0.,1.,' Inten  Rad  b/a    P.A.    XC     YC  |')
  n=0
  for line in prf:
    if line[3] > (i2-i1)*0.05:
      if line[6] == 0:
        pgsci(2)
      elif line[6] == -1:
        pgsci(3)
      else:
        pgsci(4)
      edraw(1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])
      strng='%8.2f' % line[0]
      strng=strng+'%6.1f' % line[3]
      strng=strng+'%5.2f' % line[12]
      if line[13] < 0:
        strng=strng+'%7.2f' % (line[13]+180.)
      else:
        strng=strng+'%7.2f' % line[13]
      strng=strng+'%7.1f' % line[14]
      strng=strng+'%7.1f' % line[15]
      y=y-dy
      n=n+1
#      if n < 30: pgptxt(x,y,0.,1.,strng)
      if n < 30: pgmtxt('RV',1.,y,0.,strng)
  pgsci(1)
  pgscf(2)
  return

def clean(prf):
  try:
    for n in range(len(prf)-1): 
      if prf[n][18] == 0:           # if iteration counter zero, clean
        ibot=0
        for i in range(n,0,-1):
          if prf[i][18] != 0:
            ibot=i
            break
        itop=len(prf)
        for i in range(n,len(prf)):
          if prf[i][18] != 0:
            itop=i
            break
        if ibot == 0:
          for i in range(12,15): prf[n][i]=prf[itop][i]
        elif itop >= len(prf):
          for i in range(12,15): prf[n][i]=prf[ibot][i]
        else:

# linear interp for ellipse parameters of cross-over isophote

          k=(prf[n][3]-prf[ibot][3])/(prf[itop][3]-prf[ibot][3])
          xtop=prf[itop][13]
          xbot=prf[ibot][13]
          if xbot <= xtop:
            if xtop-xbot > 90:
#            xang=((xtop-180.)+xbot)/2.
              xang=((xtop-180.)-xbot)*k+xbot
            else:
#            xang=(xtop+xbot)/2.
              xang=(xtop-xbot)*k+xbot
          else:
            if xbot-xtop > 90:
              xang=((xbot-180.)+xtop)/2.
            else:
              xang=(xbot+xtop)/2.
          prf[n][13]=xang
          for i in [12,14,15]:
            prf[n][i]=(prf[itop][i]-prf[ibot][i])*k+prf[ibot][i]
        prf[n][6]=-1.
        prf[n][18]=1

  except:
    pass

  return

# main

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: prf_edit file_name'
  print
  print 'visual editor of isophote ellipses output from efit'
  print
  print 'note: needs a .xml file, works with cleaned images'
  print
  print 'cursor commands:'
  print 'r = reset display      z = zoom in'
  print 'c = change cont        x = flag ellipse/lum point'
  print 't = toggle wd cursor   o = clean profile'
  print 'q = exit               h = this message'
  sys.exit()

filename=sys.argv[1]
if '.' not in filename: filename=filename+'.fits'

tmp=os.popen('xml_archangel -o '+filename.split('.')[0]+' sky').read()
if 'element not found' in tmp:
  print 'no sky value in .xml file - aborting'
  sys.exit()
sky=float(tmp)
sig=float(os.popen('xml_archangel -o '+filename.split('.')[0]+' skysig').read())

prf=[]
try:
  file=open(filename.split('.')[0]+'.prf','r')
  while 1:
    line=file.readline()
    if not line: break
    tmp=[]
    for x in line.split(): tmp.append(float(x))
    if tmp[13] >= 270: tmp[13]=tmp[13]-360.
    if tmp[13] > 90: tmp[13]=tmp[13]-180.
    if tmp[13] <= -270: tmp[13]=tmp[13]+360.
    if tmp[13] < -90: tmp[13]=tmp[13]+180.
#  if tmp[6] < 0: tmp[6]=abs(tmp[6])
    tmp.append(1)
    prf.append(tmp)
    xmax=tmp[3]
    xm=int(tmp[14])
    ym=int(tmp[15])
  file.close()
except:
  tmp=os.popen('xml_archangel -o '+filename.split('.')[0]+' prf').read()
  if 'element not found' in tmp:
    print 'no prf data in .xml file - aborting'
    sys.exit()
  for t in tmp.split('\n')[1:-1]:
    z=[]
    for x in t.split(): z.append(float(x))
    if z[13] >= 270: z[13]=z[13]-360.
    if z[13] > 90: z[13]=z[13]-180.
    if z[13] <= -270: z[13]=z[13]+360.
    if z[13] < -90: z[13]=z[13]+180.
    z.append(1)
    prf.append(z)
    xmax=z[3]
    xm=int(z[14])
    ym=int(z[15])

fitsobj=pyfits.open(filename,"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
hdr=fitsobj[0].header
#print hdr.items()
pix=fitsobj[0].data

if len(sys.argv) > 2:
  r2=float(sys.argv[2])
  r1=float(sys.argv[3])
else:
  if sig == 0.0: sig=0.1
  r1=sky+50.*sig
  r2=sky-0.05*(r1-sky)

x=[] ; y=[]
for j in xrange(ny):
  for i in xrange(nx):
    if str(pix[j,i]) == 'nan':
      x.append(i+1.0)
      y.append(j+1.0)
xs=numarray.array(x)
ys=numarray.array(y)

pgbeg('/xs',1,2)
pgask(0)
pgscr(0,1.,1.,1.)
pgscr(1,0.,0.,0.)
pgpap(11.5,0.9)
pgscf(2)
pgsch(1.5)
#pgvsiz(0.5,6.5,0.5,6.5)
aspect=float(ny)/float(nx)
#pgpap(0.,aspect)
xmin=0.
ymin=0.
ymax=100.
plot(prf,1,nx,xmin,xmax,ymin,ymax,sky,0)
gray(pix,1,nx,1,ny,r1,r2)
pgsci(2)
pgpt(xs,ys,-2)
pgsci(1)
eplot(prf,1,nx,1,ny)

i1=1
i2=nx
j1=1
j2=ny
xsig=5.
x0=nx/2.
y0=ny/2.
xstep=nx/2
iwin=0
iwrite=0

while 1:

  if iwin == 0:
    pgpanl(1,2)
    pgvsiz(0.5,6.5,0.5,6.5)
    pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
  else:
    pgpanl(1,1)
    pgvsiz(0.5,6.5,2.7,4.2)
    pgswin(xmin,xmax,ymax,ymin)

  d=pgband(0)

  if d[2] == '/':
    if iwrite:
      clean(prf)
      file=open('tmp.prf','w')
      for out in prf:
        strng=''
        for tmp in out[:18]: strng=strng+'%16.8e' % tmp
        file.write(strng+'\n')
      file.close()
      print 'output to tmp.prf'
    sys.exit()

  if d[2] == 'x' or d[2] == 'd':
    rmin=1.e33
    for line in prf:
      if iwin == 0:
        th=90.-180.*atan((d[0]-line[14])/(d[1]-line[15]))/pi
        rtest=((d[0]-line[14])**2+(d[1]-line[15])**2)**0.5
        rr=findr(th*pi/180.,1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])
      else:
        rtest=d[0]
        rr=line[3]
      if abs(rtest-rr) < rmin:
        rmin=abs(rtest-rr)
        imin=prf.index(line)

# set iteration flag to zero for cleaning or delete ellipse

    if d[2] == 'd':
      iwrite=1
      del prf[imin]
      plot(prf,i1,i2,xmin,xmax,ymin,ymax,sky,0)
      gray(pix,i1,i2,j1,j2,r1,r2)
      pgsci(2)
      pgpt(xs,ys,-2)
      pgsci(1)
      eplot(prf,i1,i2,j1,j2)
    else:
      if prf[imin][18] == 1:
        prf[imin][18]=0
        prf[imin][6]=0.
      else:
        prf[imin][18]=1
        prf[imin][6]=-1.
      plot(prf,i1,i2,xmin,xmax,ymin,ymax,sky,1)
      eplot(prf,i1,i2,j1,j2)

  if d[2] == 'u':
    rmin=1.e33
    for line in prf:
      if iwin == 0:
        th=90.-180.*atan((d[0]-line[14])/(d[1]-line[15]))/pi
        rtest=((d[0]-line[14])**2+(d[1]-line[15])**2)**0.5
        rr=findr(th*pi/180.,1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])
      else:
        rtest=d[0]
        rr=line[3]
      if abs(rtest-rr) < rmin:
        rmin=abs(rtest-rr)
        imin=prf.index(line)
    for i in range(imin,len(prf)):
      prf[i][18]=0                   # set iteration flag to zero for cleaning
    plot(prf,i1,i2,xmin,xmax,ymin,ymax,sky,1)
    eplot(prf,i1,i2,j1,j2)

  if d[2] == 't': iwin=abs(iwin-1)

  if d[2] == 'o':
    iwrite=1
    clean(prf)
    plot(prf,i1,i2,xmin,xmax,ymin,ymax,sky,0)
    gray(pix,i1,i2,j1,j2,r1,r2)
    pgsci(2)
    pgpt(xs,ys,-2)
    pgsci(1)
    eplot(prf,i1,i2,j1,j2)

  if d[2] == 'c':
    rold=r1
    k=d[0]*1.5/(i2-i1)+0.5-1.5*i1/(i2-i1)
    r1=r1*k
    if r1 < sky: r1=(rold-sky)/2.+sky
    r2=sky-0.05*(r1-sky)
    plot(prf,i1,i2,xmin,xmax,ymin,ymax,sky,0)
    gray(pix,i1,i2,j1,j2,r1,r2)
    pgsci(2)
    pgpt(xs,ys,-2)
    pgsci(1)
    eplot(prf,i1,i2,j1,j2)

  if d[2] == 'r':
    xsig=0.
    xstep=nx/2
    i1=1
    i2=nx
    j1=1
    j2=ny
    plot(prf,i1,i2,xmin,xmax,ymin,ymax,sky,0)
    gray(pix,i1,i2,j1,j2,r1,r2)
    pgsci(2)
    pgpt(xs,ys,-2)
    pgsci(1)
    eplot(prf,i1,i2,j1,j2)

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
    plot(prf,i1,i2,xmin,xmax,ymin,ymax,sky,0)
    gray(pix,i1,i2,j1,j2,r1,r2)
    pgsci(2)
    pgpt(xs,ys,-2)
    pgsci(1)
    eplot(prf,i1,i2,j1,j2)

  if d[2] == 'h':
    print 'r = reset display      z = zoom in'
    print 'c = change cont        x = flag ellipse/lum point'
    print 't = toggle wd cursor   o = clean profile'
    print 'd = delete ellipse     q = exit'
