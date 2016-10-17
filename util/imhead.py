#!/usr/bin/env python

import pyfits,sys,os
 
num={16:'integer',32:'real',64:'double'}

try:
  if '-h' in sys.argv or len(sys.argv) <= 1:
    raise

  if sys.argv[-1] not in os.listdir('.'):
    print 'no file found'
    raise SystemExit

  width=0
  for filename in sys.argv[1:]: width=max(width,len(filename))
  for filename in sys.argv[1:]:
    tab=pyfits.open(filename)
    hdr=tab[0].header
    print filename.rjust(width),
    print '['+str(hdr.ascardlist()['NAXIS1']).split()[2]+':'+str(hdr.ascardlist()['NAXIS2']).split()[2]+']',
    print '['+num[abs(int(str(hdr.ascardlist()['BITPIX']).split()[2]))]+']',
    try:
      print str(hdr.ascardlist()['OBJECT']).split('\'')[1]
    except:
      print

except SystemExit:
  sys.exit()
except:
  print '''
Usage: imhead file_name(s)
'''
