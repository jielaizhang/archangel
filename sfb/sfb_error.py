#!/usr/bin/env python

import sys, os.path, pyfits, time
from math import *
from xml_archangel import *
import subprocess
from pylab import *
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Ellipse

if __name__ == '__main__':

  if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
    doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    try:
      sky=float(elements['sky'][0][1])
    except:
      sky=0.
    try:
      skysig=float(elements['skysig'][0][1])
    except:
      skysig=1.

    try:
      xscale=float(elements['scale'][0][1])
    except:
      xscale=1.
    try:
      cons=float(elements['zeropoint'][0][1])
    except:
      cons=25.

    try:
      k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05,'1563':0.10,'1564':0.10,'1565':0.10,'1566':0.10,'1391':0.10,'1494':0.10}
      exptime=float(elements['exptime'][0][1])
      if exptime != 0: # exptime = 0. signals all calibration in zeropoint, no airmass
        airmass=float(elements['airmass'][0][1])
        cons=2.5*log10(exptime)+cons
        cons=cons-k[elements['filter'][0][1]]*airmass
    except:
      pass

    try:
      origin=elements['origin'][0][1]
    except:
      origin=None

    for t in elements['array']:
      if t[0]['name'] == 'prf':
        prf=[]
        data=[]
        head=[]
        for z in t[2]['axis']:
          prf.append(map(float,z[1].split('\n')))
          head.append(z[0]['name'])
        for z in range(len(prf[0])):
          err1=prf[head.index('RMSRES')][z]/(prf[head.index('NUM')][z])**0.5
          err2=skysig/(2.)**0.5 # note sqrt(2) kluge
          data.append([prf[head.index('RAD')][z],prf[head.index('INTENS')][z],1,(err1**2+err2**2)**0.5])
          intens=prf[head.index('INTENS')][z]
          err=(err1**2+err2**2)**0.5
          print prf[head.index('RAD')][z],prf[head.index('INTENS')][z],err1,err2,(err1**2+err2**2)**0.5,
          print abs(-2.5*log10((intens-sky)/(xscale**2))+cons-(-2.5*log10((intens+err1-sky)/(xscale**2))+cons)),
          print abs(-2.5*log10((intens-sky)/(xscale**2))+cons-(-2.5*log10((intens+err2-sky)/(xscale**2))+cons)),
          print abs(-2.5*log10((intens-sky)/(xscale**2))+cons-(-2.5*log10((intens+err-sky)/(xscale**2))+cons))

        tmp=array(prf)
        prf=swapaxes(tmp,1,0)
