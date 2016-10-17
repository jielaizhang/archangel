#!/usr/bin/env python

import pyfits,sys,os

if '-h' in sys.argv:
  print 'peak filename x1,x2,y1,y2 threshold'
  print
  print 'find all the peaks above threshold intensity'
  print 'if x1,x2,y1,y2 do sub-raster'
  sys.exit()

fitsobj=pyfits.open(sys.argv[1],"readonly")
hdr=fitsobj[0].header
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
pix=fitsobj[0].data

#thres=os.popen('~/archangel/scan/threshold.py '+' '.join(sys.argv[1:])).read().split('\n')
thres=os.popen('threshold '+sys.argv[1]+' 0 '+sys.argv[-1]).read().split('\n')

for z in thres:
  try:
    xc=int(z.split()[0])
    yc=int(z.split()[1])
    if xc < 5 or xc > nx-5: continue
    if yc < 5 or yc > ny-5: continue
#    print z,xc,yc
    for j in [yc-1,yc,yc+1]:
      for i in [xc-1,xc,xc+1]:
#        print i,j,pix[j-1][i-1],pix[yc-1][xc-1]
        if pix[j-1][i-1] > pix[yc-1][xc-1]: raise

    xc,yc=os.popen('centroid '+sys.argv[1]+' '+str(xc)+' '+str(yc)+' 5 '+sys.argv[-1]).read().split()
    print xc,yc,' 10 0 0 0'
  except:
    pass

