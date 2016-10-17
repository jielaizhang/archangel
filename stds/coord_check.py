#!/usr/bin/env python

import urllib, sys, os, pyfits, numarray
from math import *

def xytosky(trans,x,y):
  if len(trans) == 7:
    corr=cos(pi*(trans[3]+trans[5]*(y-trans[4]))/180.)
    return trans[0]+(trans[2]/corr)*(x-trans[1]),trans[3]+trans[5]*(y-trans[4]),
  else:
    corr=cos(pi*(trans[4]+trans[6]*(x-trans[1])+trans[7]*(y-trans[5]))/180.)
    return trans[0]+(trans[2]/corr)*(x-trans[1])+(trans[3]/corr)*(y-trans[5]), \
           trans[4]+trans[6]*(x-trans[1])+trans[7]*(y-trans[5])

def skytoxy(trans,ra,dec):
  c=cos(pi*(trans[4]+trans[6]*(400.-trans[1])+trans[7]*(400.-trans[5]))/180.)
  t1=c*ra/trans[2]-c*trans[0]/trans[2]-trans[3]*dec/(trans[2]*trans[7])
  t1=t1+trans[3]*trans[4]/(trans[2]*trans[7])+trans[1]*(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
  t1=t1/(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
  t2=(dec-trans[4]-trans[6]*(t1-trans[1]))/trans[7]+trans[5]
  c=cos(pi*(trans[4]+trans[6]*(t1-trans[1])+trans[7]*(t2-trans[5]))/180.)
  t1=c*ra/trans[2]-c*trans[0]/trans[2]-trans[3]*dec/(trans[2]*trans[7])
  t1=t1+trans[3]*trans[4]/(trans[2]*trans[7])+trans[1]*(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
  t1=t1/(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
  t2=(dec-trans[4]-trans[6]*(t1-trans[1]))/trans[7]+trans[5]
  return t1,t2

if sys.argv[-1] == '-h':
  print 'this routine takes a file (in.tmp) of coords and downloads PSS-II images to'
  print 'check coords and update, needs a files of coords in : format first'
  print 'object is the seach center'
  sys.exit()

stars=[tmp.split() for tmp in open('in.tmp','r').readlines()]

tmp=os.popen('hms '+stars[0][1]+':'+stars[0][2]+':'+stars[0][3]+' '+stars[0][4]+':'+stars[0][5]+':'+stars[0][6]).read()
ra=tmp.split()[0]
dec=tmp.split()[1]

if '-f' in sys.argv:
  data=urllib.urlopen('http://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_blue&r='+  \
                      ra+'&d='+dec+'&e=J2000&h=15.0&w=15.0&f=fits&c=none&fov=NONE&v3=').read()
  file=open('junk.fits','w')
  file.write(data[:-1]+'\n')
  file.close()

fitsobj=pyfits.open('junk.fits',"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
hdr=fitsobj[0].header
trans=[hdr['CRVAL1'],hdr['CRPIX1'],hdr['CD1_1'],hdr['CD1_2'], \
       hdr['CRVAL2'],hdr['CRPIX2'],hdr['CD2_1'],hdr['CD2_2']]

tmp=os.popen('sky_box -f junk.fits').read()
sky=float(tmp.split()[2])
skysig=float(tmp.split()[3])

tmp=os.popen('gasp_images -f junk.fits '+str(sky)+' '+str(5.*skysig)+' 20 true').read()

scan=[]
for z in tmp.split('\n')[:-1]:
  scan.append(map(float,z.split()))

out=open('out.tmp','w')
tmp=open('tmp.tmp','w')
for n,star in enumerate(stars):
  t=os.popen('hms '+star[1]+':'+star[2]+':'+star[3]+' '+star[4]+':'+star[5]+':'+star[6]).read()
  ra=float(t.split()[0])
  dec=float(t.split()[1])
  x,y=skytoxy(trans,ra,dec)
  if x < 0 or x > nx or y < 0 or y > ny: continue
  tot=0.
  for z in scan:
    rr=((x-z[0])**2+(y-z[1])**2)**0.5
    if tot < z[2]/rr**2:
      tot=z[2]/rr**2
      xmin=z[0]
      ymin=z[1]

  ra,dec=xytosky(trans,xmin,ymin)
  print >> out,star[0],os.popen('hms -d '+str(ra)+' '+str(dec)).read()[:-1].replace('h','').replace('d','').replace('m','').replace('s','')

  z1=os.popen('hms -d '+str(ra)+' '+str(dec)).read()[:-1].replace('h ',':').replace('d ',':').replace('m ',':').replace('s','')
  z2=star[1]+':'+star[2]+':'+star[3]+' '+star[4]+':'+star[5]+':'+star[6]
  test1=os.popen('hms '+z1).read()
  test2=os.popen('hms '+z2).read()
  if test1 == test2:
    print >> tmp,star[0],os.popen('hms -d '+str(ra)+' '+str(dec)).read()[:-1].replace('h','').replace('d','').replace('m','').replace('s',''),'3'
  else:
    print >> tmp,star[0],os.popen('hms -d '+str(ra)+' '+str(dec)).read()[:-1].replace('h','').replace('d','').replace('m','').replace('s',''),'4'
    print >> tmp,' '.join(star),'2'

out.close()
tmp.close()
os.system('source do_label tmp.tmp')
os.system('probe -l junk.fits')
