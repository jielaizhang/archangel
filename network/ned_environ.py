#!/usr/bin/env python

import urllib, sys, re, time

if '-h' in sys.argv:
  print './ned_environ.py master_list'
  sys.exit()

files=[tmp[:-1] for tmp in open(sys.argv[-1],'r').readlines()]

for id in files:
  data=urllib.urlopen('http://ned.ipac.caltech.edu/cgi-bin/denv?obj='+id+'&cz=&Ho=73&OM=0.27&OL=0.73&dist=&plot=1').read()

  for n,line in enumerate(data.split('\n')):
    if 'Sample' in line:
      break
  else:
    print id,' no data'
    continue

  print id,
  for z in re.sub('<.*?>',' ',data.split('\n')[n+1]).split():
    print z,
  print

  time.sleep(2.)


