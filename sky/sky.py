#!/usr/bin/env python

import os,sys,math

if '.' not in sys.argv[-1]:
  prefix=sys.argv[-1]
  endfix='fits'
else:
  prefix=sys.argv[-1].split('.')[0]
  endfix=sys.argv[-1].split('.')[1]

cmd='keys -p '+prefix+'.'+endfix+' | grep NAXIS1'
print cmd
nx=int(os.popen(cmd).read().split()[2])
cmd='keys -p '+prefix+'.'+endfix+' | grep NAXIS2'
print cmd
ny=int(os.popen(cmd).read().split()[2])
box='5'
if nx > 200: box='10'
if nx > 500: box='20'
if '-x' in sys.argv:
  cmd='sky_box -x '+sys.argv[-1]
  print cmd
  sky=os.popen(cmd).read()
else:
  cmd='sky_box -r '+prefix+'.clean '+box
  print cmd
  sky=os.popen(cmd).read()
  cmd='xml_archangel -e '+prefix+' nsky '+sky.split()[4]
  print cmd
  tmp=os.popen(cmd).read()
cmd='xml_archangel -e '+prefix+' sky '+sky.split()[2]
print cmd
tmp=os.popen(cmd).read()
cmd='xml_archangel -e '+prefix+' skysig '+sky.split()[3]
print cmd
tmp=os.popen(cmd).read()
