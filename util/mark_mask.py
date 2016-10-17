#!/usr/bin/env python

import sys, os, time
import astropy.io.fits as pyfits
from numpy import *
from math import *
from xml.dom import minidom, Node
from xml_archangel import *

if __name__ == '__main__':

  if '-h' in sys.argv:
    print 'mark_mask mark_file file_to_repixel'
    print
    print 'output to file_to_repixel.repixel'
    sys.exit()

  doc = minidom.parse(sys.argv[-2].split('.')[0]+'.xml')
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)
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

  fitsobj=pyfits.open(sys.argv[-1],"readonly")
  nx=fitsobj[0].header['NAXIS1']
  ny=fitsobj[0].header['NAXIS2']
  pix=fitsobj[0].data
  fitsobj.close()
  out=zeros((nx,ny),'Float32')
  out=out*sqrt(-1.)

  for i,j in marks: out[j-1][i-1]=pix[j-1][i-1]

  if os.path.exists(sys.argv[-1].split('.')[0]+'.repixel'):
    os.remove(sys.argv[-1].split('.')[0]+'.repixel')
  fitsobj=pyfits.HDUList()
  hdu=pyfits.PrimaryHDU()
  hdu.data=out
  fitsobj.append(hdu)
  fitsobj.writeto(sys.argv[-1].split('.')[0]+'.repixel')
