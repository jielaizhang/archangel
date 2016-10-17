#!/usr/bin/env python

import urllib, sys, os, os.path, pyfits, time
import numpy.numarray as numarray
from math import *

def xytosky(trans,x,y):
  if len(trans) < 7:
    corr=cos(pi*(trans[3]+trans[5]*(y-trans[4]))/180.)
    return trans[0]+(trans[2]/corr)*(x-trans[1]),trans[3]+trans[5]*(y-trans[4]),
  else:
    corr=cos(pi*(trans[4]+trans[6]*(x-trans[1])+trans[7]*(y-trans[5]))/180.)
    return trans[0]+(trans[2]/corr)*(x-trans[1])+(trans[3]/corr)*(y-trans[5]), \
           trans[4]+trans[6]*(x-trans[1])+trans[7]*(y-trans[5])

def skytoxy(trans,ra,dec):
  y=trans[4]+(dec-trans[3])/trans[5]
  corr=cos(pi*(trans[3]+trans[5]*(y-trans[4]))/180.)
  x=trans[1]+(ra-trans[0])*corr/trans[2]
  return x,y

def top_right(center):
  dra=(-256./3600.)/(cos(pi*float(ra_dec[3])/180.))
  ddec=256./3600.
  if center:
    name=(str(float(ra_dec[2]))+'+'+str(float(ra_dec[3]))).replace(' ','')
  else:
    name=(str(float(ra_dec[2])+dra)+'+'+str(float(ra_dec[3])+ddec)).replace(' ','')
  page=urllib.urlopen('http://irsa.ipac.caltech.edu/cgi-bin/2MASS/IM/nph-im_pos?id=f0&type=at&'+ \
                      'ds=asky&POS='+name+'&band='+band).read()
  for n,t in enumerate(page.split('\n')):
    if 'Click to download FITS file' in t:
      break
  place=page.split('\n')[n+1].split('http')[2].split('"')[0][9:]
  print 'top right   ',place.replace('%2F','/').split('/')[-1],
  if not os.path.exists(place.replace('%2F','/').split('/')[-1]):
    print 'downloading',
    pixels=urllib.urlopen('http://'+place.replace('%2F','/')).read()
    file=open(place.replace('%2F','/').split('/')[-1],'w')
    file.write(pixels)
    file.close()
  fitsobj=pyfits.open(place.replace('%2F','/').split('/')[-1],"readonly")
  hdr=fitsobj[0].header
  trans=[hdr['CRVAL1'],hdr['CRPIX1'],hdr['CDELT1'], \
         hdr['CRVAL2'],hdr['CRPIX2'],hdr['CDELT2']]
  pix=fitsobj[0].data
  sky=float(hdr['SKYVAL'])
  zpt=float(hdr['MAGZP'])
  x2,y2=skytoxy(trans,float(ra_dec[2])+dra,float(ra_dec[3])+ddec)
  xm=int(round(x2))
  ym=int(round(y2))
  print xm,ym
  for j in range(1,min(ym,508)):
    for i in range(8,min(xm,508)):
      xint=(pix[j][i]-sky)*10.**((zpt-float(magzp))/-2.5)
      data[512-ym+j][512-xm+i]=xint
#  hdu=pyfits.PrimaryHDU(data)
#  hdr=hdu.header
#  hdu.writeto('tr.fits')

def bottom_left(center):
  dra=(256./3600.)/(cos(pi*float(ra_dec[3])/180.))
  ddec=-256./3600.
  if center:
    name=(str(float(ra_dec[2]))+'+'+str(float(ra_dec[3]))).replace(' ','')
  else:
    name=(str(float(ra_dec[2])+dra)+'+'+str(float(ra_dec[3])+ddec)).replace(' ','')
  page=urllib.urlopen('http://irsa.ipac.caltech.edu/cgi-bin/2MASS/IM/nph-im_pos?id=f0&type=at&'+ \
                      'ds=asky&POS='+name+'&band='+band).read()
  for n,t in enumerate(page.split('\n')):
    if 'Click to download FITS file' in t:
      break
  place=page.split('\n')[n+1].split('http')[2].split('"')[0][9:]
  print 'bottom left ',place.replace('%2F','/').split('/')[-1],
  if not os.path.exists(place.replace('%2F','/').split('/')[-1]):
    print 'downloading',
    pixels=urllib.urlopen('http://'+place.replace('%2F','/')).read()
    file=open(place.replace('%2F','/').split('/')[-1],'w')
    file.write(pixels)
    file.close()
  fitsobj=pyfits.open(place.replace('%2F','/').split('/')[-1],"readonly")
  hdr=fitsobj[0].header
  trans=[hdr['CRVAL1'],hdr['CRPIX1'],hdr['CDELT1'], \
         hdr['CRVAL2'],hdr['CRPIX2'],hdr['CDELT2']]
  pix=fitsobj[0].data
  sky=float(hdr['SKYVAL'])
  zpt=float(hdr['MAGZP'])
  x2,y2=skytoxy(trans,float(ra_dec[2])+dra,float(ra_dec[3])+ddec)
  xm=int(round(x2))
  ym=int(round(y2))
  print xm,ym
  ny=int(hdr['NAXIS2'])
  for j in range(ym,min((ym+512),ny)):
    for i in range(xm,508):
      xint=(pix[j][i]-sky)*10.**((zpt-float(magzp))/-2.5)
      data[j-ym][i-xm]=xint
#  hdu=pyfits.PrimaryHDU(data)
#  hdr=hdu.header
#  hdu.writeto('bl.fits')

def top_left(center):
  dra=(256./3600.)/(cos(pi*float(ra_dec[3])/180.))
  ddec=256./3600.
  if center:
    name=(str(float(ra_dec[2]))+'+'+str(float(ra_dec[3]))).replace(' ','')
  else:
    name=(str(float(ra_dec[2])+dra)+'+'+str(float(ra_dec[3])+ddec)).replace(' ','')
  page=urllib.urlopen('http://irsa.ipac.caltech.edu/cgi-bin/2MASS/IM/nph-im_pos?id=f0&type=at&'+ \
                      'ds=asky&POS='+name+'&band='+band).read()
  for n,t in enumerate(page.split('\n')):
    if 'Click to download FITS file' in t:
      break
  place=page.split('\n')[n+1].split('http')[2].split('"')[0][9:]
  print 'top left    ',place.replace('%2F','/').split('/')[-1],
  if not os.path.exists(place.replace('%2F','/').split('/')[-1]):
    print 'downloading',
    pixels=urllib.urlopen('http://'+place.replace('%2F','/')).read()
    file=open(place.replace('%2F','/').split('/')[-1],'w')
    file.write(pixels)
    file.close()
  fitsobj=pyfits.open(place.replace('%2F','/').split('/')[-1],"readonly")
  hdr=fitsobj[0].header
  trans=[hdr['CRVAL1'],hdr['CRPIX1'],hdr['CDELT1'], \
         hdr['CRVAL2'],hdr['CRPIX2'],hdr['CDELT2']]
  pix=fitsobj[0].data
  sky=float(hdr['SKYVAL'])
  zpt=float(hdr['MAGZP'])
  x2,y2=skytoxy(trans,float(ra_dec[2])+dra,float(ra_dec[3])+ddec)
  xm=int(round(x2))
  ym=int(round(y2))
  print xm,ym
  ny=int(hdr['NAXIS2'])
  for j in range(5,min(ym,ny)):
    for i in range(xm,506):
      xint=(pix[j][i]-sky)*10.**((zpt-float(magzp))/-2.5)
      data[512-ym+j][i-xm]=xint
#  hdu=pyfits.PrimaryHDU(data)
#  hdr=hdu.header
#  hdu.writeto('tl.fits')

def bottom_right(center):
  dra=(-256./3600.)/(cos(pi*float(ra_dec[3])/180.))
  ddec=-256./3600.
  if center:
    name=(str(float(ra_dec[2]))+'+'+str(float(ra_dec[3]))).replace(' ','')
  else:
    name=(str(float(ra_dec[2])+dra)+'+'+str(float(ra_dec[3])+ddec)).replace(' ','')
  page=urllib.urlopen('http://irsa.ipac.caltech.edu/cgi-bin/2MASS/IM/nph-im_pos?id=f0&type=at&'+ \
                      'ds=asky&POS='+name+'&band='+band).read()
  for n,t in enumerate(page.split('\n')):
    if 'Click to download FITS file' in t:
      break
  place=page.split('\n')[n+1].split('http')[2].split('"')[0][9:]
  print 'bottom right',place.replace('%2F','/').split('/')[-1],
  if not os.path.exists(place.replace('%2F','/').split('/')[-1]):
    print 'downloading',
    pixels=urllib.urlopen('http://'+place.replace('%2F','/')).read()
    file=open(place.replace('%2F','/').split('/')[-1],'w')
    file.write(pixels)
    file.close()
  fitsobj=pyfits.open(place.replace('%2F','/').split('/')[-1],"readonly")
  hdr=fitsobj[0].header
  trans=[hdr['CRVAL1'],hdr['CRPIX1'],hdr['CDELT1'], \
         hdr['CRVAL2'],hdr['CRPIX2'],hdr['CDELT2']]
  pix=fitsobj[0].data
  sky=float(hdr['SKYVAL'])
  zpt=float(hdr['MAGZP'])
  x2,y2=skytoxy(trans,float(ra_dec[2])+dra,float(ra_dec[3])+ddec)
  xm=int(round(x2))
  ym=int(round(y2))
  print xm,ym
  ny=int(hdr['NAXIS2'])
  for j in range(ym,min((ym+512),ny)):
    for i in range(9,xm):
      xint=(pix[j][i]-sky)*10.**((zpt-float(magzp))/-2.5)
      data[j-ym][512-xm+i]=xint
#  hdu=pyfits.PrimaryHDU(data)
#  hdr=hdu.header
#  hdu.writeto('br.fits')

if __name__ == "__main__":

  if '-h' in sys.argv or len(sys.argv) < 2:
    print './2mass_stitch op band galaxy_ID'
    print
    print 'grabs 2MASS frames around galaxy and stitchs 512x512 image'
    print
    print 'options: -n = no display'
    print '         -r = do not erase raw frames'
    print '   -nosleep = do not sleep for 30 secs between frames'
    print '       band = A means J+H+K'
    sys.exit()

  for band in ['J','H','K']:
    if band != sys.argv[-2] and sys.argv[-2] != 'A': continue

    data=numarray.resize([float('nan')], (512,512))

    ra_dec=os.popen('/Users/js/archangel/network/ned_coords.py '+sys.argv[-1]).read().split()
    name=(ra_dec[1]+'+'+ra_dec[2]).replace(' ','')

    page=urllib.urlopen('http://irsa.ipac.caltech.edu/cgi-bin/2MASS/IM/nph-im_pos?id=f0&type=at&'+ \
                        'ds=asky&POS='+name+'&band='+band).read()
    for n,t in enumerate(page.split('\n')):
      if 'Click to download FITS file' in t:
        break
    place=page.split('\n')[n+1].split('http')[2].split('"')[0][9:]
    print 'primary file',place.replace('%2F','/').split('/')[-1]
    if not os.path.exists(place.replace('%2F','/').split('/')[-1]):
      print 'downloading',
      pixels=urllib.urlopen('http://'+place.replace('%2F','/')).read()
      file=open(place.replace('%2F','/').split('/')[-1],'w')
      file.write(pixels)
      file.close()
    fitsobj=pyfits.open(place.replace('%2F','/').split('/')[-1],"readonly")
    hdr=fitsobj[0].header
    trans=[hdr['CRVAL1'],hdr['CRPIX1'],hdr['CDELT1'], \
           hdr['CRVAL2'],hdr['CRPIX2'],hdr['CDELT2']]
    pix=fitsobj[0].data
    sky_o=float(hdr['SKYVAL'])
    magzp=hdr['MAGZP']
    x,y=skytoxy(trans,float(ra_dec[2]),float(ra_dec[3]))
    xc=int(round(x))
    yc=int(round(y))
    print 'galaxy center',xc,yc,

    if xc < 256 and yc > 512+256:
      print 'top left'
      print

      top_left(0)
      top_right(0)
      bottom_left(0)
      bottom_right(1)

    if xc >= 256 and yc > 512+256:
      print 'top right'
      print

      top_left(0)
      bottom_right(0)
      top_right(0)
      bottom_left(1)

    if xc < 256 and yc <= 256:
      print 'bottom left'
      print

      bottom_left(0)
      bottom_right(0)
      top_left(0)
      top_right(1)

    if xc >= 256 and yc < 256:
      print 'bottom right'
      print

      bottom_left(0)
      bottom_right(0)
      top_right(0)
      top_left(1)

    if xc >= 256 and yc >= 256 and yc <= 512+256:
      print 'center right'
      print

      top_right(0)
      bottom_left(0)
      bottom_right(0)
      top_left(1)

    if xc < 256 and yc >= 256 and yc <= 512+256:
      print 'center left'
      print

      top_right(0)
      bottom_left(0)
      top_left(0)
      bottom_right(1)

    if os.path.exists(sys.argv[-1]+'_'+band.lower()+'.fits'): os.remove(sys.argv[-1]+'_'+band.lower()+'.fits')
    hdu=pyfits.PrimaryHDU(data)
    hdr=hdu.header
    hdr.update('ORIGIN','2MASS')
    hdr.update('OBJECT',sys.argv[-1].upper())
    hdr.update('FILTER',band)
    hdr.update('MAGZP',magzp)
    print 'output to',sys.argv[-1]+'_'+band.lower()+'.fits'
    if band == 'J' and '-n' not in sys.argv: os.system('probe '+sys.argv[-1]+'_'+band.lower()+'.fits')
    hdu.writeto(sys.argv[-1]+'_'+band.lower()+'.fits')
    if '-r' not in sys.argv:
      print 'rm a'+band+'*.fits'
      os.system('rm a'+band+'*.fits')
      if '-nosleep' not in sys.argv:
        print 'sleeping 30 secs'
        time.sleep(30)
    print
