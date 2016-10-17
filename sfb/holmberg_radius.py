#!/usr/bin/env python

import sys
from numpy import *
from xml_archangel import *

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

if __name__ == '__main__':

  if '-h' in sys.argv:
    print './holmberg_radius op master_file'
    print
    print 'finds Holmberg radius (26.5 B mag arcsecs^-2)'
    print 'output in arcsecs and kpc'
    print
    print 'options: -i = use different isophote'
    sys.exit()

  file=open(sys.argv[-1])
  if '-i' in sys.argv:
    holm=float(sys.argv[-2])
  else:
    holm=26.5

  while 1:
    line=file.readline()
    if not line: break
    master=line.split()[0]

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
#      cons=float(elements['zeropoint'][0][1])
      try:
        kpc=float(elements['cosmology_corrected_scale_kpc_arcsec'][0][1])
      except:
        kpc=1.
      try:
        zpt=float(elements['zeropoint'][0][1])
      except:
        zpt=0.
      try:
        tot=float(elements['tot_mag_sfb'][0][1])
      except:
        tot=0.

      for t in elements['array']:
        if t[0]['name'] == 'prf':
          prf=[]
          for z in t[2]['axis']:
            prf.append(map(float,z[1].split('\n')))
          tmp=array(prf)
          prf=swapaxes(tmp,1,0)
          break

      for t in elements['array']:
        if t[0]['name'] == 'sfb':
          sfb=[]
          for z in t[2]['axis']:
            sfb.append(map(float,z[1].split('\n')))
          tmp=array(sfb)
          sfb=swapaxes(tmp,1,0)
          break
      else:
        print master,'no_sfb'
        continue

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

      for z in sfb:
        if z[1] > holm:
          holm_rad=interp(z[1],last_z[1],z[0],last_z[0],holm)
          print master,'%.2f' % (holm_rad),
          print '%.2f' % (kpc*holm_rad),
          break
        last_z=z
      else:
        holm_rad=interp(sfb[-1][1],sfb[-2][1],sfb[-1][0],sfb[-2][0],holm)
        print master+'#','%.2f' % (holm_rad),
        print '%.2f' % (kpc*holm_rad),

      for z in ept:
        if z[0] > holm_rad:
          print '%.2f' % (interp(z[0],last_z[0],z[1],last_z[1],holm_rad)+zpt),
          mag=interp(z[0],last_z[0],z[1],last_z[1],holm_rad)+zpt
          print '%.2f' % (100.*((10.**(mag/-2.5))/(10.**(tot/-2.5))))
          break
        last_z=z
      else:
        print '0. 0.'
