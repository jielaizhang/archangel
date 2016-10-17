#!/usr/bin/env python

import sys
from math import *
from ppgplot import *
try:
  import numpy.numarray as numarray
except:
  import numarray
import pyfits

def gray(pix,i1,i2,j1,j2,r1,r2):
  pgeras()
#  pgpap(10.,aspect)
  pgswin(i1,i2,j1,j2)
#  pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
  pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
  pgswin(i1+0.5,i2+0.5,j1+0.5,j2+0.5)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
#  tmp='%6.1f' % r2
#  pgptxt(i1+1.5,(j1+1.5)-0.10*(j2-j1),0.,0.5,tmp)
#  tmp='%6.1f' % r1
#  pgptxt(i2+1.5,(j1+1.5)-0.10*(j2-j1),0.,0.5,tmp)
  return

def outside(x2,y2,x3,y3,x4,y4,x5,y5,x,y):
# test points on edges on box or outside box, return true if inside or on box
  if y <= max(y2,y3,y4,y5) and y >= min(y2,y3,y4,y5) and x <= max(x2,x3,x4,x5) and x >= min(x2,x3,x4,x5):
    return 1
  else:
    return 0

def inside(x2,y2,x3,y3,x4,y4,x5,y5,x,y):
# is x,y inside or on the box
  b1=int(perp(x2,x3,y2,y3,x,y)/abs(perp(x2,x3,y2,y3,x,y)))
  b2=int(perp(x3,x4,y3,y4,x,y)/abs(perp(x3,x4,y3,y4,x,y)))
  b3=int(perp(x4,x5,y4,y5,x,y)/abs(perp(x4,x5,y4,y5,x,y)))
  b4=int(perp(x5,x2,y5,y2,x,y)/abs(perp(x5,x2,y5,y2,x,y)))
  if not (b1+b2+b3+b4) and y <= max(y2,y3,y4,y5) and y >= min(y2,y3,y4,y5) and \
     x <= max(x2,x3,x4,x5) and x >= min(x2,x3,x4,x5):
    return 1
  else:
    return 0

def corner(r,s,edge):
  for x,y in edge:
    if x >= r-0.5 and x <= r+0.5 and y >= s-0.5 and y <= s+0.5: return x,y
  return 0

def piece(vert):
  det=0.
  for i in range(len(vert)):
    j=i+1
    if j >= len(vert): j=0
    det=det+(vert[i][0]*vert[j][1]-vert[j][0]*vert[i][1])
  return abs(det/2.)

def perp(x1,x2,y1,y2,x,y):
# horizontal line
  if round(y2-y1,5) == 0:
    return y-y1
# vertical line
  if round(x2-x1,5) == 0:
    return x-x1
# regular line
  m=(y2-y1)/(x2-x1)
  b=y2-x2*(y2-y1)/(x2-x1)
  c=y+x/m
  r=(c-b)/(m+1./m)
  s=m*r+b
  d=((r-x)**2+(s-y)**2)**0.5
  if r <= x:
    return d
  else:
    return -d

def box():
  pgsci(4)
  pgmove(xm,ym)
  pgdraw(x1,y1)
  pgmove(x2,y2)
  pgdraw(x3,y3)
  pgdraw(x4,y4)
  pgdraw(x5,y5)
  pgdraw(x2,y2)
  pgmove(x1,y1)
  pgdraw(x2,y2)
  pgmove(x1,y1)
  pgdraw(x3,y3)
  pgmove(x1,y1)
  pgdraw(x4,y4)
  pgmove(x1,y1)
  pgdraw(x5,y5)
  pgsci(0)

def edges(w,z,xm,ym,d,pos_ang):
  x1=d*cos(pos_ang)+xm
  y1=d*sin(pos_ang)+ym
  r=(w**2+z**2)**0.5
  ang=pi/2.-atan(z/w)-(pi/2.-pos_ang)
  x2=x1-r*sin(ang)
  y2=y1+r*cos(ang)
  x3=x1-r*cos(ang+pi/2.-2.*pos_ang)
  y3=y1+r*sin(ang+pi/2.-2.*pos_ang)
  x4=x1+r*sin(ang)
  y4=y1-r*cos(ang)
  x5=x1+r*cos(ang+pi/2.-2.*pos_ang)
  y5=y1-r*sin(ang+pi/2.-2.*pos_ang)
  d1=abs(min(x2,x3,x4,x5)-max(x2,x3,x4,x5))
  d2=abs(min(y2,y3,y4,y5)-max(y2,y3,y4,y5))
  delta=max(d1,d2)
  left=int(x1-0.60*delta)
  right=int(x1+0.6*delta)
  bottom=int(y1-0.60*delta)
  top=int(y1+0.6*delta)
  return x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,left,right,bottom,top

if sys.argv[1] == '-h':
  print 'surveyor xc yc dist pos_ang width depth filename x y'
  print
  print 'Usage: x & y to see individual pixel'

try:
  xm=float(sys.argv[1])
  ym=float(sys.argv[2])
  d=float(sys.argv[3])
  pos_ang=float(sys.argv[4])*pi/180.
  w=float(sys.argv[5])
  z=float(sys.argv[6])
except:
  print 'input error'
  sys.exit()

pgbeg('/xs',1,1)
pgask(0)
pgscr(0,1.,1.,1.)
pgscr(1,0.,0.,0.)
pgscf(2)
pgpap(10.0,1.0)

fitsobj=pyfits.open(sys.argv[7],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
aspect=1.
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()

file=open(sys.argv[7].split('.')[0]+'.sky','r')
line=file.readline()
xsky=float(line.split()[0])
skysig=float(line.split()[1])
r1=xsky+50.*skysig
r2=xsky-0.05*(r1-xsky)
file.close()

file=open(sys.argv[7].split('.')[0]+'.cal','r')
line=file.readline()
scale=float(line.split()[0])
zpt=float(line.split()[1])

x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,left,right,bottom,top=edges(w,z,xm,ym,d,pos_ang)

try:
  xc=float(sys.argv[8])
  yc=float(sys.argv[9])
  pgswin(xc-1.,xc+1.,yc-1.,yc+1.)
except:
  xc=0 ; yc=0
  pgswin(left,right,bottom,top)

gray(pix,left,right,bottom,top,r1,r2)
box()

pgsch(0.6)
results=[]
sum=0.
lum=0.
x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,left,right,bottom,top=edges(w,z,xm,ym,d,pos_ang)
for i in range(int(left),int(right)+1):
  pgsci(3)
  r=i
  pgmove(r-0.5,bottom)
  pgdraw(r-0.5,top)

  for j in range(int(bottom),int(top)+1):
    pgsci(3)
    s=j
    pgmove(left,s-0.5)
    pgdraw(right,s-0.5)

# find edge points and test for position
    x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,t1,t2,t3,t4=edges(w+sqrt(0.5),z+sqrt(0.5),xm,ym,d,pos_ang)

# center of pixel is inside extended box (sqrt(r) of a pixel)
    if inside(x2,y2,x3,y3,x4,y4,x5,y5,r,s):

# redo real box size, check if pixel center off top or bottom by 0.5
      x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,t1,t2,t3,t4=edges(w,z,xm,ym,d,pos_ang)
      if s >= max(y2,y3,y4,y5)+0.5 or s <= min(y2,y3,y4,y5)-0.5: continue

      coords=[(x2,y2),(x3,y3),(x4,y4),(x5,y5)]
      try:
        a=abs(min(abs(perp(x2,x3,y2,y3,r,s)), \
                  abs(perp(x3,x4,y3,y4,r,s)), \
                  abs(perp(x4,x5,y4,y5,r,s)), \
                  abs(perp(x5,x2,y5,y2,r,s))))
      except:
        a=0.

      if a <= sqrt(0.5) or corner(r,s,[(x2,y2),(x3,y3),(x4,y4),(x5,y5)]): # i'm an edge or corner
        tmp=[]

# find the crossing points and check if on pixel edge
        for i in range(len(coords)):
          j=i+1
          if j == len(coords): j=0

# find if edge crosses pixel and determine which pixel edge
          if abs(perp(coords[i][0],coords[j][0],coords[i][1],coords[j][1],r,s)) < sqrt(0.5):

            if round(coords[j][1]-coords[i][1],5) == 0: # horziontal line
              x=r+0.5
              y=coords[i][1]
              if outside(x2,y2,x3,y3,x4,y4,x5,y5,x,y):
                tmp.append((x,y))
              x=r-0.5
              if outside(x2,y2,x3,y3,x4,y4,x5,y5,x,y):
                tmp.append((x,y))

            elif round(coords[j][0]-coords[i][0],5) == 0: # vertical line
              y=s+0.5
              x=coords[i][0]
              if outside(x2,y2,x3,y3,x4,y4,x5,y5,x,y):
                tmp.append((x,y))
              y=s-0.5
              if outside(x2,y2,x3,y3,x4,y4,x5,y5,x,y):
                tmp.append((x,y))

            else: # regular line
              m=(coords[j][1]-coords[i][1])/(coords[j][0]-coords[i][0])
              b=coords[j][1]-coords[j][0]*(coords[j][1]-coords[i][1])/(coords[j][0]-coords[i][0])
              x=(s+0.5-b)/m
              if x >= r-0.5 and x <= r+0.5 and outside(x2,y2,x3,y3,x4,y4,x5,y5,x,m*x+b):
                tmp.append((x,m*x+b))
              x=(s-0.5-b)/m
              if x >= r-0.5 and x <= r+0.5 and outside(x2,y2,x3,y3,x4,y4,x5,y5,x,m*x+b):
                tmp.append((x,m*x+b))
              y=m*(r+0.5)+b
              if y >= s-0.5 and y <= s+0.5 and outside(x2,y2,x3,y3,x4,y4,x5,y5,(y-b)/m,y):
                tmp.append(((y-b)/m,y))
              y=m*(r-0.5)+b
              if y >= s-0.5 and y <= s+0.5 and outside(x2,y2,x3,y3,x4,y4,x5,y5,(y-b)/m,y):
                tmp.append(((y-b)/m,y))

# find pixel corners that are inside box
        for x,y in [(r-0.5,s-0.5),(r-0.5,s+0.5),(r+0.5,s-0.5),(r+0.5,s+0.5)]:
          if inside(x2,y2,x3,y3,x4,y4,x5,y5,x,y):
            tmp.append((x,y))

# put in the corner if needed
        if corner(r,s,[(x2,y2),(x3,y3),(x4,y4),(x5,y5)]):
          tmp.append(corner(r,s,[(x2,y2),(x3,y3),(x4,y4),(x5,y5)]))

# sort vertices, pop off first one
        if not tmp:
          area=0.
        else:
          x0=tmp[0][0]
          y0=tmp[0][1]
          vert=[tmp[0]]
          tmp.remove(tmp[0])

          for i in range(len(tmp)):
            dmin=1.e33
            for x,y in tmp:
              dd=((x0-x)**2+(y0-y)**2)**0.5
              if dd < dmin:
                t=(x,y)
                dmin=dd
            try:
              x0=t[0]
              y0=t[1]
              vert.append(t)
              tmp.remove(t)
            except:
              pass
          area=1.*piece(vert)

        if r == xc and s == yc:
          print 'end vert',vert
          print piece(vert),pix[s][r]

      else: # i'm well inside the box
        area=1.
        if r == xc and s == yc: print pix[s][r]

      if corner(r,s,[(x2,y2),(x3,y3),(x4,y4),(x5,y5)]): # i'm a corner
        pgsci(4)
      else:
        pgsci(2)

      pgptxt(r,s,0.,0.5,'%3.3i' % int(100.*area))
      sum=sum+area*scale**2
      if str(pix[s][r]) != 'nan': lum=lum+area*(pix[s][r]-xsky)

print w,sum,lum,-2.5*log10(lum/sum)+zpt
try:
  for i in numarray.arange(xc-0.5,xc+0.5,0.1):
    pgmove(i,yc-0.5)
    pgdraw(i,yc+0.5)
  for i in numarray.arange(yc-0.5,yc+0.5,0.1):
    pgmove(xc-0.5,i)
    pgdraw(xc+0.5,i)
except:
  pass
