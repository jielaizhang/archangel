#!/usr/bin/env python

import sys, os, math
try:
  import numpy.numarray as numarray
except:
  import numarray
import pyfits
from xml_archangel import *

def findr(t,eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  c1=bsq*(math.cos(t))**2+asq*(math.sin(t))**2
  c2=(asq-bsq)*2*math.sin(t)*math.cos(t)
  c3=bsq*(math.sin(t))**2+asq*(math.cos(t))**2
  c4=asq*bsq
  return (c4/(c1*(math.cos(d))**2+c2*math.sin(d)*math.cos(d)+c3*(math.sin(d))**2))**0.5

if sys.argv[1] == '-h' or len(sys.argv) < 2:
  print 'grid_phot op marks_file data_file radius'
  print
  print 'does grid photometry from marks in xml file on fits file'
  print 'output= I_grid, -2.5log(I_grid), aperture value for rmax, rmax'
  print
  print 'options: -m = use marks from marks_file'
  print '         radius (optional force radius)'
  sys.exit()

last=0
if '-m' in sys.argv:
  try:
    float(sys.argv[-1])
    last=-1
  except:
    last=0
  os.system('xml_archangel -o '+sys.argv[-2+last].split('.')[0]+' marks | xml_archangel -a '+sys.argv[-1+last].split()[0]+' marks') 

fitsobj=pyfits.open(sys.argv[-1+last],"readonly")
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()

doc = minidom.parse(sys.argv[-1+last].split('.')[0]+'.xml')
rootNode = doc.documentElement
elements=xml_read(rootNode).walk(rootNode)
xsky=float(elements['sky'][0][1])

for t in elements['array']:
  if t[0]['name'] == 'marks':
      marks=[]
      for z in t[2]['axis']:
        marks.append(map(int,z[1].split('\n')))
      tmp=numarray.array(marks)
      marks=numarray.swapaxes(tmp,1,0)
      break

for t in elements['array']:
  if t[0]['name'] == 'prf': # ellipse data
    prf=[]
    head=[]
    pts=[]
    for z in t[2]['axis']:
      head.append(z[0]['name'])
      pts.append(map(float,z[1].split('\n')))
    for z in range(len(pts[0])):
      tmp=[]
      for w in head:
        tmp.append(pts[head.index(w)][z])
      prf.append(tmp)

for t in elements['array']:
  if t[0]['name'] == 'ept':
    ept=[]
    for z in t[2]['axis']:
      ept.append(map(float,z[1].split('\n')))
    tmp=numarray.array(ept)
    ept=numarray.swapaxes(tmp,1,0)
    break
else:
  print 'no ept data in .xml file - aborting'
  sys.exit()

if last:
  rmax=float(sys.argv[-1])
else:
  rmax=0.
  for xdata,ydata in marks:
    rmin=1.e33
    for line in prf:
      th=90.-180.*math.atan((xdata-line[14])/(ydata-line[15]))/math.pi
      rtest=((xdata-line[14])**2+(ydata-line[15])**2)**0.5
      rr=findr(th*math.pi/180.,1.-line[12],line[3],-line[13]*math.pi/180.,line[14],line[15])
      if abs(rtest-rr) < rmin:
        rmin=abs(rtest-rr)
        imin=prf.index(line)
    if prf[imin][3] > rmax: rmax=prf[imin+1][3]

for z in ept:
  if round(z[0],1) == round(rmax,1):
    ephot=z[1]
    break

tmp=0.
for i,j in marks:
  if pix[j-1][i-1] == pix[j-1][i-1]: tmp=tmp+pix[j-1][i-1]-xsky
print '%.1f' % tmp, '%.3f' % (-2.5*math.log10(tmp)),'%.3f' % ephot,'%.1f' % rmax
