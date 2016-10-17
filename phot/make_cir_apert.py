#!/usr/bin/env python

import sys, os, math

if sys.argv[1] == '-h':
  print '''
Usage: make_cir_apert option fits_file mag_limit

options: -s = make an s.tmp file for probe
         -c = make an aperture file for calib_phot
'''
  sys.exit()

sky=os.popen('xml_archangel -o '+sys.argv[-2].split('.')[0]+' sky').read()[:-1]
skysig=float(os.popen('xml_archangel -o '+sys.argv[-2].split('.')[0]+' skysig').read())
scan=os.popen('gasp_images -f '+sys.argv[-2]+' '+sky+' '+str(10*skysig)+' 20 1').read()

if '-s' in sys.argv:
  for z in scan.split('\n')[:-1]:
    if float(z.split()[5]) > float(sys.argv[-1]): continue
    print z.split()[0],
    print z.split()[1],
    print 10*int(z.split()[2]),
    print '0.0 0.0 ',
    print z.split()[5],
    print '1'
    print z.split()[0],
    print z.split()[1],
    r=1.5*(10*int(z.split()[2])/math.pi)**0.5
    print math.pi*r**2,
    print '0.0 0.0 ',
    print z.split()[5],
    print '-1'
    print z.split()[0],
    print z.split()[1],
    r=10.+1.5*(10*int(z.split()[2])/math.pi)**0.5
    print math.pi*r**2,
    print '0.0 0.0 ',
    print z.split()[5],
    print '-1'

else:
  for z in scan.split('\n')[:-1]:
    if float(z.split()[5]) > float(sys.argv[-1]): continue
    print z.split()[0],
    print z.split()[1],
    print (10*int(z.split()[2])/math.pi)**0.5,
    print 1.5*(10*int(z.split()[2])/math.pi)**0.5,
    print 10.+1.5*(10*int(z.split()[2])/math.pi)**0.5
