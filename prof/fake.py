#!/usr/bin/env python

import os, sys

if '-h' in sys.argv:
  print 'Usage: fake option file_name_prefix'
  print
  print 'code builds fake.in file output from XML file'
  print
  print 'Options: -h = this mesage'
  print '         -m = produce model file (.model)'
  print '         -s = produce subtraction file (.sub)'
  print '         -c = fill in a cleaned file (.fake)'
  print '         -x = do a clean on .clean, then sub on .fake'
  print '         -q = quiet'
  print
  print 'note: -c wants .clean file > .fake'
  print 'model and subtract want .fake > .sub'
  sys.exit()

prefix=sys.argv[-1].split('.')[0]
try:
  suffix=sys.argv[-1].split('.')[1]
except:
  suffix=None

if not os.path.exists(prefix+'.xml'):
  print 'no XML file,',prefix
  sys.exit()

if '-q' not in sys.argv: print 'xml_archangel -o '+prefix+' sky > fake.in'
os.system('xml_archangel -o '+prefix+' sky > fake.in')

if '-q' not in sys.argv: print 'xml_archangel -o '+prefix+' prf | lines 2- >> fake.in'
os.system('xml_archangel -o '+prefix+' prf | lines 2- >> fake.in')

if '-c' in sys.argv or '-x' in sys.argv:
  if '-q' not in sys.argv: print 'make_fake -c '+prefix+'.clean'
  os.system('make_fake -c '+prefix+'.clean')

if '-s' in sys.argv or '-x' in sys.argv:
  if '-q' not in sys.argv: print 'make_fake -s '+prefix+'.fake'
  os.system('make_fake -s '+prefix+'.fake')
  sky=os.popen('xml_archangel -o '+prefix+' sky').read()
#  if '-q' not in sys.argv: print 'imarith "'+prefix+'.sub - '+sky.split()[-1]+' '+prefix+'.sub"'
#  os.system('imarith "'+prefix+'.sub - '+sky.split()[-1]+' '+prefix+'.sub"')

if '-m' in sys.argv:
  if '-q' not in sys.argv: print 'make_fake -m '+prefix+'.fits'
  os.system('make_fake -m '+prefix+'.fits')

if '-q' not in sys.argv: 
  if '-c' in sys.argv: 
    os.system('probe '+prefix+'.fake')
  if '-s' in sys.argv or '-x' in sys.argv: 
    os.system('probe -t '+prefix+'.sub')
  if '-m' in sys.argv: 
    os.system('probe '+prefix+'.model')

if os.path.isfile('fake.in'): os.remove('fake.in')
