#!/usr/bin/env python

import urllib, sys, re

if '-h' in sys.argv or len(sys.argv) < 2:
  print './url_read.py op webpage_URL'
  print
  print 'reads the HTML of a webpage'
  print
  print 'options: -s = strip HTML tags'
  sys.exit()

data=urllib.urlopen(sys.argv[-1]).read()
if sys.argv[1] == '-s':
  print re.sub('<.*?>','',data.replace('\n',' '))
else:
  print data
