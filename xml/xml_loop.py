#!/usr/bin/env python

import sys, os

lines=[tmp for tmp in open(sys.argv[1],'r').readlines()]
for line in lines:
  print line[:-1].split('.xml')[0],sys.argv[-1],
  print os.popen('xml_archangel -o '+line[:-1]+' '+sys.argv[-1]).read()[:-1]
