#!/usr/bin/env python

import sys, os, time
from xml.dom import minidom, Node
from xml_archangel import *

if __name__ == '__main__':

  filename=sys.argv[-1]
  print 'grid_dump two_color.fits > 1.tmp'
  os.system('grid_dump two_color.fits > 1.tmp')
  print 'pread 1.tmp 0 1 > s.tmp'
  os.system('pread 1.tmp 0 1 > s.tmp')
  doc = minidom.parse(filename+'.xml')
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)
  scale=(float(elements['scale'][0][1]))**2.
  cmd='grid_dump -m '+filename+'.fits | opstrm c c r '+elements['sky'][0][1]+ \
      ' - '+elements['exptime'][0][1]+' / '+str(scale)+' / Flog -2.5 x '+  \
      elements['zeropoint'][0][1]+' + = > 2.tmp'
  print cmd
  os.system(cmd)
  print 'paste 1.tmp 2.tmp | grep -v nan > '+sys.argv[-1]+'.color_sfb'
  os.system('paste -d" " 1.tmp 2.tmp | grep -v nan | opstrm c c r f5.2f = s s r = > '+sys.argv[-1]+'.color_sfb')
