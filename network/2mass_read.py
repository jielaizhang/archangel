#!/usr/bin/env python

import urllib, sys, os

if '-h' in sys.argv or len(sys.argv) < 2:
  print '2mass_read op J/H/K name or ra&dec'
  print
  print 'options: -q = do not display'
  print '         -x = just get filename'
  print
  print 'note: ra&dec must be decimal ra with plus sign decimal dec'
  sys.exit()

name=sys.argv[-1]

if '-x' in sys.argv:
  band='J'
else:
  band=sys.argv[-2]

url='http://irsa.ipac.caltech.edu/cgi-bin/2MASS/IM/nph-im_pos?id=f0&type=at&'+ \
    'ds=asky&POS='+name+'&band='+band
data=urllib.urlopen(url).read()

if 'Image Service Error' in data:
  print 'no image, aborting'
  sys.exit()

for n,t in enumerate(data.split('\n')):
  if 'Click to download FITS file' in t:
    break
place=data.split('\n')[n+1].split('http')[2].split('"')[0][9:]
print place.replace('%2F','/')
if '-x' in sys.argv: sys.exit()

pixels=urllib.urlopen('http://'+place.replace('%2F','/')).read()
file=open(place.replace('%2F','/').split('/')[-1],'w')
#file.write(data[:m-1]+'\n')
file.write(pixels)
file.close()
if '-q' not in sys.argv: os.system('probe '+place.replace('%2F','/').split('/')[-1])
