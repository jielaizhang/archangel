#! /usr/bin/env python

import sys, os.path, math
from pylab import *
from xml.dom import minidom, Node
from xml_archangel import *

if '-h' in sys.argv:
  print './gen_rad_sfb.py op name'
  print 'seaches file directory for xml file with similar name'
  print
  print 'options: -s = dont search'
  print '         -e = output in r^1/4 space'
  print '         -f = use input as list of filenames'
  print '         -r = output in raw arcsecs/mags'
  sys.exit()

if '-f' in sys.argv:
  filex=[tmp[:-1] for tmp in open(sys.argv[-1],'r').readlines()]
else:
  filex=[sys.argv[-1]]

for file in filex:

  if '-s' in sys.argv:
    name=sys.argv[-1]
    root='.'
  else:
    try:
      for root, dirs, files in os.walk('.'):
        for name in files:
          if 'xml' not in name: continue
          if file in name:
            raise
      else:
        print file,'no file found'
        sys.exit()
    except:
      pass

  doc = minidom.parse(root+'/'+name.split('.')[0]+'.xml')
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)
  scale=float(elements['cosmology_corrected_scale_kpc_arcsec'][0][1])
  try:
    ext=float(elements['gal_extinc_J'][0][1])
  except:
    print name,'failed to find gal_extinc_J'
    sys.exit()

  if '-r' in sys.argv:
    scale=1.
    ext=0.

  try:
    for t in elements['array']:
      if t[0]['name'] == 'prf':
        prf=[]
        for z in t[2]['axis']:
          prf.append(map(float,z[1].split('\n')))
        tmp=array(prf)
        prf=swapaxes(tmp,1,0)
        break
    else:
      print 'no prf data in .xml file - aborting'
      sys.exit()
  except:
    raise
    print 'problem with data in .xml file - aborting'
    sys.exit()

  try:
    for t in elements['array']:
      if t[0]['name'] == 'sfb':
        sfb=[]
        for z in t[2]['axis']:
          sfb.append(map(float,z[1].split('\n')))
        tmp=array(sfb)
        sfb=swapaxes(tmp,1,0)
        break
    else:
      print 'no sfb data in .xml file - aborting'
      sys.exit()
  except:
    raise
    print 'problem with data in .xml file - aborting'
    sys.exit()

  for x in sfb:
    for y in prf:
      if y[3] >= x[0]:
        if '-e' in sys.argv:
          print '%6.2f' % (scale*(x[0]*x[0]*(1.-y[12]))**0.5)**0.25,
        elif '-r' in sys.argv:
          print '%6.2f' % (scale*(x[0]*x[0]*(1.-y[12]))**0.5),
        else:
          print '%6.2f' % math.log10(scale*(x[0]*x[0]*(1.-y[12]))**0.5),
        print '%6.3f' % (x[1]-ext),'%1.1i' % x[2],x[3],'%.3f' % y[12],name.split('.')[0]
        break
