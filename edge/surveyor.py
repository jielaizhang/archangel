#!/usr/bin/env python

import sys
from math import *
import numarray
import pyfits

def xperp(m,b,x,y):
  if m != 0.:
    c=y+x/m
    r=(c-b)/(m+1./m)
  else:
    r=x
  s=m*r+b
  d=((r-x)**2+(s-y)**2)**0.5
  if r <= x:
    return d
  else:
    return -d

def linfit(fit):
  sum=0.0
  sumx=0.0
  sumy=0.0
  sumxy=0.0
  sumx2=0.0
  sumy2=0.0
  n=0
  for tmp in fit:
    n+=1
    sum=sum+(1./tmp[2]**2)
    sumx=sumx+(1./tmp[2]**2)*tmp[0]
    sumy=sumy+(1./tmp[2]**2)*tmp[1]
    sumxy=sumxy+(1./tmp[2]**2)*tmp[0]*tmp[1]
    sumx2=sumx2+(1./tmp[2]**2)*tmp[0]*tmp[0]
    sumy2=sumy2+(1./tmp[2]**2)*tmp[1]*tmp[1]
  dex=sum*sumx2-sumx*sumx
# y intersect -- a
  a=(sumx2*sumy-sumx*sumxy)/dex
# slope -- b
  b=(sum*sumxy-sumx*sumy)/dex
# varience
  var=(sumy2+a*a*sum+b*b*sumx2-2.*(a*sumy+b*sumxy-a*b*sumx))/(n-2)
  if var < 0.: var=0.
# correlation coefficient -- r
  r=(sum*sumxy-sumx*sumy)/((dex*(sum*sumy2-sumy*sumy))**0.5)
# sigma b
  sigb=(var*sumx2/dex)**0.5
# sigma m
  sigm=(var*sum/dex)**0.5
  sig=0.
  for tmp in fit:
    z=a+b*tmp[0]
    sig=sig+(z-tmp[1])**2
  sig=(sig/(n-1))**.5
  return a,b,r,sigb,sigm,sig

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

# main

if sys.argv[1] == '-h':
  print 'surveyor xc yc start stop pos_ang width depth filename'
  print
  print 'Usage: xc yc pos_ang from scan, start and stop radii, iterate over width'

try:
  xm=float(sys.argv[1])
  ym=float(sys.argv[2])
  start=float(sys.argv[3])
  stop=float(sys.argv[4])
  pos_ang=float(sys.argv[5])*pi/180.
  w=float(sys.argv[6])
  z=float(sys.argv[7])
except:
  print 'input error'
  sys.exit()

fitsobj=pyfits.open(sys.argv[8],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
aspect=1.
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()

file=open(sys.argv[8].split('.')[0]+'.sky','r')
line=file.readline()
xsky=float(line.split()[0])
skysig=float(line.split()[1])
r1=xsky+50.*skysig
r2=xsky-0.05*(r1-xsky)
file.close()

file=open(sys.argv[8].split('.')[0]+'.cal','r')
line=file.readline()
scale=float(line.split()[0])
zpt=float(line.split()[1])

for d in numarray.arange(start,stop,5.):
  x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,left,right,bottom,top=edges(w,z,xm,ym,d,pos_ang)

  w=float(sys.argv[6])+2.
  results=[]
  while (w > 2):
    sum=0.
    lum=0.
    w=w-2.
    for pos_ang in (float(sys.argv[5])*pi/180.,float(sys.argv[5])*pi/180.+pi):
      x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,left,right,bottom,top=edges(w,z,xm,ym,d,pos_ang)
      for i in range(int(left),int(right)+1):
        r=i
        for j in range(int(bottom),int(top)+1):
          s=j

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

            else: # i'm well inside the box
              area=1.

            sum=sum+area*scale**2
            if str(pix[s][r]) != 'nan': lum=lum+area*(pix[s][r]-xsky)

#  print w,sum,lum,-2.5*log10(lum/sum)+zpt
    results.append([w,sum,lum,-2.5*log10(lum/sum)+zpt])

  x=[] ; y=[]; data=[]
  for t in results:
    x.append(t[0])
    y.append(t[-1])
    data.append([t[0],t[-1],0.,'o',0,0.])

  fit=[]
  for t in data:
    if t[4] == 0: fit.append([t[0],t[1],1.])
  a,b,r,sigb,sigm,sig=linfit(fit)
  ax=a
  bx=b
  for n in range(10):
    sig=[]
    xmean=0.
    for t in data:
      if t[4] == 0: 
        xmean=xmean+xperp(bx,ax,t[0],t[1])
        sig.append(xperp(bx,ax,t[0],t[1]))
    xmean=xmean/len(sig)
    sigma=0.
    for tmp in sig:
      sigma=sigma+(xmean-tmp)**2
    sigma=(sigma/(len(sig)-1.))**0.5
    fit=[]
    for t in data:
      if t[4] == 0: 
        ss=abs(xperp(bx,ax,t[0],t[1])/sigma)
        if ss < .5: ss=.5
        fit.append([t[0],t[1],ss])
    ax,bx,rx,sigbx,sigmx,sigx=linfit(fit)
  print d,ax
