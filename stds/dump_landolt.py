#!/usr/bin/env python

import sys
file=open('/Users/js/stds/landolt.new','r')
while 1:
  line=file.readline()
  if not line: break
  print line[:12].rstrip().replace(' ','_').replace('RU','Rubin'),
  v=float(line.split()[-5])
  b=float(line.split()[-3])+v
  u=float(line.split()[-4])+b
  r=v-float(line.split()[-2])
  i=r-float(line.split()[-1])
  fil={'U':u,'B':b,'V':v,'R':r,'I':i}
  print fil[sys.argv[-1]]
