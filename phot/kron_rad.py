#!/usr/bin/env python

import sys
from numpy import *
from xml_archangel import *

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

if __name__ == '__main__':

  if '-h' in sys.argv:
    print 'calculate Kron radii (at 20 J sfb from master list'
    sys.exit()

  file=open('master.2MASS_kron','r')

  while 1:
    line=file.readline()
    if not line: break
    master=line.split()[0]+'_j'

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

      for z in sfb:
        if z[1] > 20:
#          print z
          kron_rad=interp(z[1],last_z[1],z[0],last_z[0],20.)
          print master,'%.2f' % (2.*interp(z[1],last_z[1],z[0],last_z[0],20.)),
          break
        last_z=z

      for z in prf:
        if z[3] > kron_rad:
#          print z
          print '%.2f' % (2.*kron_rad*(1.-z[12])),
          break

      for z in ept:
        if z[0] > kron_rad:
          print '%.2f' % (interp(z[0],last_z[0],z[1],last_z[1],kron_rad)+cons)
          break
        last_z=z
