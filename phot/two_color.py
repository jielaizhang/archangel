#!/usr/bin/env python

import sys, os, os.path
from math import *
from numpy import *
import astropy.io.fits as pyfits
#os.system('setenv PYRAF_NO_DISPLAY 1')
import pyraf
from xml_archangel import *

if sys.argv[1] == '-h':
  print 'two_color blue_file red_file radius color_slope color_zpt sigma_cut'
  print 'output to two_color.fits'
  sys.exit()

k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05, \
   '1563':0.10,'1564':0.10,'1565':0.10,'1566':0.10,'1391':0.10,'1494':0.10}

doc = minidom.parse(sys.argv[1].split('.')[0]+'.xml')
rootNode = doc.documentElement
elements=xml_read(rootNode).walk(rootNode)

blue_sky=float(elements['sky'][0][1])
blue_sig=float(elements['skysig'][0][1])
blue_expt=float(elements['exptime'][0][1])
blue_k=k[sys.argv[1].split('.')[0][-1]]*float(elements['airmass'][0][1])
scale=float(elements['scale'][0][1])

doc = minidom.parse(sys.argv[2].split('.')[0]+'.xml')
rootNode = doc.documentElement
elements=xml_read(rootNode).walk(rootNode)

red_sky=float(elements['sky'][0][1])
red_sig=float(elements['skysig'][0][1])
red_expt=float(elements['exptime'][0][1])
red_k=k[sys.argv[2].split('.')[0][-1]]*float(elements['airmass'][0][1])

for t in elements['array']:
  if t[0]['name'] == 'prf':
    prf=[]
    for z in t[2]['axis']:
      prf.append(map(float,z[1].split('\n')))
    tmp=array(prf)
    prf=swapaxes(tmp,1,0)
    break

xc=int(prf[4][14])
yc=int(prf[4][15])
rad=int(sys.argv[-4])
cm=float(sys.argv[-3])
cb=float(sys.argv[-2])
xsig=float(sys.argv[-1])

tmp=os.popen('offset -q '+sys.argv[1].split('.')[0]+'.fits '+sys.argv[2].split('.')[0]+'.fits').read()
xs,ys=map(float,tmp.split())

os.system('cp '+sys.argv[1]+' tmp1.fits')
os.system('cp '+sys.argv[2]+' tmp2.fits')
pyraf.iraf.imshift('tmp2.fits','shift.fits',-xs,-ys)

pyraf.iraf.boxcar('tmp1.fits','two_color1.fits',3,3)
pyraf.iraf.boxcar('shift.fits','two_color2.fits',3,3)
#pyraf.iraf.imarith('two_color1.fits','-','two_color2.fits','two_color.fits')

fitsobj=pyfits.open('two_color1.fits',"readonly")
pix1=fitsobj[0].data
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
fitsobj.close()

fitsobj=pyfits.open('two_color2.fits',"readonly")
pix2=fitsobj[0].data
fitsobj.close()

os.remove('shift.fits')
os.remove('tmp1.fits')
os.remove('tmp2.fits')
os.remove('two_color1.fits')
os.remove('two_color2.fits')

out=zeros((nx,ny),'Float32')
out=out*sqrt(-1.)

for j in range(max(2,yc-rad),min(ny-2,yc+rad)):
  for i in range(max(2,xc-rad),min(nx-2,xc+rad)):
    blue=0. ; red=0.
    for m in [-1,0,1]:
      for n in [-1,0,1]:
        blue=blue+pix1[j+m][i+n]/9.
        red=red+pix2[j+m][i+n]/9.
    if blue-blue_sky > xsig*blue_sig and red-red_sky > xsig*red_sig:
      tmp=(-2.5*log10((blue-blue_sky)/blue_expt)-blue_k)- \
          (-2.5*log10((red-red_sky)/red_expt)-red_k)
#      out[j-(yc-rad)][i-(xc-rad)]=cm*tmp+cb
      out[j][i]=cm*tmp+cb

fitsobj = pyfits.HDUList()
hdu = pyfits.PrimaryHDU()
hdu.data = out
fitsobj.append(hdu)
if os.path.exists('two_color.fits'): os.remove('two_color.fits')
fitsobj.writeto('two_color.fits')
