#!/usr/bin/env python

import urllib, sys, os

if '-h' in sys.argv or len(sys.argv) < 2:
  print 'dss_read filter (J/F) name or dss_read -c ra dec'
  sys.exit()

if sys.argv[1] != '-c':
  print 'doing NED search'
  filename=sys.argv[-1]
  data=urllib.urlopen('http://nedwww.ipac.caltech.edu/cgi-bin/nph-objsearch?objname='+sys.argv[-1]+ \
                      '&extend=no&out_csys=Equatorial&out_equinox=J2000.0&obj_sort=RA+or+Longitude&of=pre_text&'+ \
                      'zv_breaker=30000.0&list_limit=5&img_stamp=YES').read()
  for t in data.split('\n'):
    if 'Equatorial' in t and 'J2000' in t:
      ra=t.split()[2]
      dec=t.split()[3]
      break
  else:
    print 'not found in NED, aborting'
    sys.exit()
else:
  filename='dss'
  ra=sys.argv[-2]
  dec=sys.argv[-1]

if sys.argv[1] == 'F':
  filter='poss2ukstu_red'
  fil='F'
else:
  filter='poss2ukstu_blue'
  fil='J'

print 'searching DSS'
data=urllib.urlopen('http://archive.stsci.edu/cgi-bin/dss_search?v='+filter+'&r='+  \
                    ra+'&d='+dec+'&e=J2000&h=15.0&w=15.0&f=fits&c=none&fov=NONE&v3=').read()
#m=data.index('XTENSION')

print 'outputing to',filename+'_'+fil+'.fits'
file=open(filename+'_'+fil+'.fits','w')
#file.write(data[:m-1]+'\n')
file.write(data[:-1]+'\n')
file.close()
if '-tmp' in sys.argv:
  tmp=os.popen('probe '+filename+'_'+fil+'.fits').read()
  os.system('rm '+filename+'_'+fil+'.fits')
