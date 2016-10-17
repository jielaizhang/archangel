#!/usr/bin/env python

import sys, os, time, pyfits
from numpy import *
from math import *
from xml.dom import minidom, Node
from xml_archangel import *

def new_pixel(xc,yc,sc1,sc2):
  width=sc2/(2.*sc1)
  i=int(xc+0.5)
  j=int(yc+0.5)
  tmp=0.
  size=0.
  for jj in [-1,0,+1]:
    for ii in [-1,0,+1]:
      if pix[j+jj][i+ii] != pix[j+jj][i+ii]: continue
#      print max(0.,width-(abs(xc-(i+ii))-0.5)),
#      print max(0.,width-(abs(yc-(j+jj))-0.5)),
#      print max(0.,width-(abs(xc-(i+ii))-0.5))*max(0.,width-(abs(yc-(j+jj))-0.5))
      tmp=tmp+max(0.,width-(abs(xc-(i+ii))-0.5))*max(0.,width-(abs(yc-(j+jj))-0.5))*pix[j+jj][i+ii]
      size=size+max(0.,width-(abs(xc-(i+ii))-0.5))*max(0.,width-(abs(yc-(j+jj))-0.5))
  try:
    return tmp/size
  except:
    return 'nan'

if __name__ == '__main__':

  doc = minidom.parse(sys.argv[1].split('.')[0]+'.xml')
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)
  sc2=float(elements['scale'][0][1])
  try:
    for t in elements['array']:
      if t[0]['name'] == 'marks': # ellipse data
        marks=[]
        head=[]
        pts=[]
        for z in t[2]['axis']:
          head.append(z[0]['name'])
          pts.append(map(float,z[1].split('\n')))
        for z in range(len(pts[0])):
          tmp=[]
          for w in head:
            tmp.append(pts[head.index(w)][z])
          marks.append(tmp)
  except:
    print 'no marks'
    sys.exit()

  doc = minidom.parse(sys.argv[2].split('.')[0]+'.xml')
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)
  sc1=float(elements['scale'][0][1])

  cx=float(sys.argv[-4])
  mx=float(sys.argv[-3])
  cy=float(sys.argv[-2])
  my=float(sys.argv[-1])

  fitsobj=pyfits.open(sys.argv[1],"readonly")
  nx=fitsobj[0].header['NAXIS1']
  ny=fitsobj[0].header['NAXIS2']
  fitsobj.close()
  out=zeros((nx,ny),'Float32')
  out=out*sqrt(-1.)
  fitsobj=pyfits.open(sys.argv[2],"readonly")
  pix=fitsobj[0].data
  fitsobj.close()

  for i,j in marks:
    out[j-1][i-1]=new_pixel((mx*i+cx)-1.,(my*j+cy)-1.,sc1,sc2)

  if os.path.exists(sys.argv[2].split('.')[0]+'.repixel'):
    os.remove(sys.argv[2].split('.')[0]+'.repixel')
  fitsobj=pyfits.HDUList()
  hdu=pyfits.PrimaryHDU()
  hdu.data=out
  fitsobj.append(hdu)
  fitsobj.writeto(sys.argv[2].split('.')[0]+'.repixel')
