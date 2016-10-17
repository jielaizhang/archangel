#!/usr/bin/env python

import sys
from numpy import *
from xml_archangel import *

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

if __name__ == '__main__':

  if '-h' in sys.argv:
    print './kron.py op kron_rad file_prefix'
    print
    print 'calculate Kron mags from K files at 20 mag arcsecs^-2'
    print
    print 'options: -r = use given semi-major axis in arcsecs'
    print 'options: -f = use file list'
    sys.exit()

  if '-f' in sys.argv:
    files=open(sys.argv[-1],'r').readlines()
  else:
    files=[sys.argv[-1]]

  for master in files:

    try:
      for root, dirs, files in os.walk('.'):
        for name in files:
          if 'xml' not in name: continue
          if master in name:
            raise
    except:
      pass

    if os.path.exists(root+'/'+master+'.xml'):
      doc = minidom.parse(root+'/'+master+'.xml')
      rootNode = doc.documentElement
      elements=xml_read(rootNode).walk(rootNode)
      scale=float(elements['scale'][0][1])
      cons=float(elements['zeropoint'][0][1])

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

      for t in elements['array']:
        if t[0]['name'] == 'ept':
          ept=[]
          head=[]
          pts=[]
          for z in t[2]['axis']:
            head.append(z[0]['name'])
            pts.append(map(float,z[1].split('\n')))
          for z in range(len(pts[0])):
            tmp=[]
            for w in head:
              tmp.append(pts[head.index(w)][z])
            ept.append(tmp)
          break
      else:
        print 'no ept data in .xml file - aborting'
        sys.exit()

    if '-r' in sys.argv:
      kron_rad=float(sys.argv[-2])/scale
      print master,'%7.2f' % (2.*kron_rad),
    else:
      for z in sfb:
        if z[1] > 20:
#        print z
          kron_rad=interp(z[1],last_z[1],z[0],last_z[0],20.)
          print master,'%7.2f' % (2.*interp(z[1],last_z[1],z[0],last_z[0],20.)),
          break
        last_z=z

    for z in prf:
      if z[3] > kron_rad:
#        print z
        print '%7.2f' % (2.*kron_rad*(1.-z[12])),
        break

    for z in ept:
#      print z[0],last_z[0],z[1]+cons,last_z[1]+cons,kron_rad
      if z[0] > kron_rad:
        print '%6.2f' % (interp(z[0],last_z[0],z[1],last_z[1],kron_rad)+cons)
        break
      last_z=z
