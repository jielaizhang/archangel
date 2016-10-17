#!/usr/bin/env python

import sys,os,os.path

def do_ned(prefix):

  cmd='ned_xml '+prefix.split('_')[0]+' '+' '.join(sys.argv[2:])
  tmp=os.popen(cmd).read()

  for z in tmp.split('\n')[:-1]:
    if 'not found' not in z:
      cmd='xml_archangel -e '+prefix+' '+z.split()[1].replace('/','_')+' "'+' '.join(z.split()[2:])+'"'
      print cmd
      os.system(cmd)
  return

if '-f' in sys.argv:
  files=[tmp[:-1] for tmp in open(sys.argv[2],'r').readlines()]
  for file in files:
    prefix=file.split('_ch1')[0]
    do_ned(prefix)
else:
  prefix=sys.argv[1]
  do_ned(prefix)
