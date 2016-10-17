#!/usr/bin/env python

import urllib, sys, os

if '-h' in sys.argv or len(sys.argv) < 2:
  print 'ned_coords galaxy_id'
  print 'outputs 2000 coords as gal RA Dec'
  print 
  print 'options: -f = use master file'
  sys.exit()

if '-f' in sys.argv:

  files=[tmp[:-1] for tmp in open(sys.argv[-1],'r').readlines()]
  for file in files:
    lines=os.popen('ned_xml -a '+file).read().split('\n')
    print file,
    for line in lines:
      if line.split()[1] == 'pos_ra_equ_J2000_d':
        print line.split()[2],
      if line.split()[1] == 'pos_dec_equ_J2000_d':
        print line.split()[2]
        break
    sys.stdout.flush()

else:

  lines=os.popen('ned_xml -a '+sys.argv[-1]).read().split('\n')
  print sys.argv[-1],
  for line in lines:
    if line.split()[1] == 'pos_ra_equ_J2000_d':
      print line.split()[2],
    if line.split()[1] == 'pos_dec_equ_J2000_d':
      print line.split()[2]
      break
