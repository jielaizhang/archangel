#!/usr//bin/env python

import os,sys,string

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: quick_scan op data_file sigma\n'
  print 'quick threshold scan of a data file, sky and sigma determined\n'
  print 'options:  -h = this message'
  sys.exit()

print '\nsky_box -f '+sys.argv[1]
sky=string.split(os.popen('sky_box -f '+sys.argv[1]).read())
print 'sky = %5.1f' % float(sky[2]),
print 'sigma = %5.1f' % float(sky[3])

if len(sys.argv) > 2:
  sig=float(sys.argv[2])
else:
  sig=5.

print '\ngasp_images -f '+sys.argv[1]+' '+sky[2]+' '+str(sig*float(sky[3]))+' 10 false > s.tmp'
os.system('gasp_images -f '+sys.argv[1]+' '+sky[2]+' '+str(sig*float(sky[3]))+' 10 false > s.tmp')
out=os.popen('wc s.tmp').read()
print '\n'+string.split(out)[0]+' targets found\n'
print '    xc     yc     npix   ecc  posang      mag'
print os.popen('cat s.tmp').read()
