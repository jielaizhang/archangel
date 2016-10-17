#!/usr/bin/env python

import sys,os
import astropy.io.fits as pyfits
 
try:
  if '-h' in sys.argv or len(sys.argv) <= 1:
    raise

  try:
    file=sys.argv[2]
    if '.' not in file:
      file=file+'.fits'
    tab=pyfits.open(file,'update')
# tab.info()
  except:
    print 'file error'
    raise SystemExit

  if '-p' in sys.argv:
    i=0
    while 1:
      try:
        hdr=tab[i].header
        if i == 0:
          print '\nPRIMARY (PrimaryHDU):\n'
        else:
          print '\n',hdr['extname'],'('+hdr['xtension']+'):\n'
        for n in hdr.ascardlist():
          print n
        i=i+1
      except:
        sys.exit()

  if '-d' in sys.argv:
    i=0
    while 1:
      try:
        hdr=tab[i].header
        if hdr.has_key(sys.argv[-1]): break
        i=i+1
      except:
        print 'keyword',sys.argv[-1],'not found'
        sys.exit()
    del hdr.ascardlist()[sys.argv[-1]]
    tab.flush()
    tab.close()
    sys.exit()

  if '-c' in sys.argv:
    hdr=tab[0].header
    try:
      float(sys.argv[4])
      hdr.update(sys.argv[3],float(sys.argv[4]))
    except:
      hdr.update(sys.argv[3],' '.join(sys.argv[4:]))
    tab.flush()
    tab.close()
    sys.exit()

except SystemExit:
  sys.exit()
except:
  print '''
Usage: keys option file_name

Options: -p = print all keys
         -c = change key (option file_name key value)
         -d = delete key'''

#  hdr=tab[1].header
#  hdr.update('COMMENT','FITS (Flexible Image Transport System)')
#  try:
#    del hdr.ascardlist()['COMMENT']
#  except:
#    print 'no keyword'
