#!/usr/bin/env python

import os, sys

lines=[tmp.split() for tmp in open(sys.argv[-1],'r').readlines()]

dd=30./(60.*60.)
for line in lines:
  ra=float(line[-2])
  dec=float(line[-1])

  if '-c' in sys.argv:

    cmd='"SELECT TOP 50 cModelMag_u,cModelMag_g,cModelMag_r,cModelMag_i,cModelMag_z,ra,dec '+ \
      'FROM Galaxy '+ \
      'WHERE '+ \
      'ra BETWEEN '+str(ra-dd)+' and '+str(ra+dd)+' AND dec BETWEEN '+str(dec-dd)+' and '+str(dec+dd)+'"'

  else:

    cmd='"SELECT TOP 50 petroMag_u,petroMag_g,petroMag_r,petroMag_i,petroMag_z,ra,dec '+ \
      'FROM Galaxy '+ \
      'WHERE '+ \
      'ra BETWEEN '+str(ra-dd)+' and '+str(ra+dd)+' AND dec BETWEEN '+str(dec-dd)+' and '+str(dec+dd)+'"'

  back=os.popen('~/archangel/sdss/sqlcl.py -q '+cmd).readlines()

  rmin=1.e33
  for z in back[2:]:
    rr=((float(z.split(',')[-2])-ra)**2.+(float(z.split(',')[-1])-dec)**2.)**0.5
    if rr < rmin:
      out=z
      rmin=rr

  print line[0],
  try:
    if rmin > 10.: raise
    for z in out.split(',')[:5]:
      print '%6.3f' % float(z),
    print '%5.2f' % (60.*60.*rmin),
  except:
    print 'None None None None None None',
  print
