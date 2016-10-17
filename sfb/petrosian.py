#!/usr/bin/env python

import sys
from xml_archangel import *

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

if __name__ == '__main__':

  if sys.argv[1] == '-h':
    print 'calculate total mag from petrosian value, 2*eta(0.2)'
    sys.exit()

  eta=0.2

  try:
    for root, dirs, files in os.walk('.'):
      for name in files:
        if 'xml' not in name: continue
        if sys.argv[-1] in name:
          raise
    else:
      print sys.argv[-1],'no file found'
      sys.exit()
  except:
    pass

  if os.path.exists(root+'/'+sys.argv[-1].split('.')[0]+'.xml'):
    doc = minidom.parse(root+'/'+sys.argv[-1].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    try:
      half=float(elements['tot_mag_half_rad'][0][1])
    except:
      print 'no half light radius'
      sys.exit()

    for t in elements['array']:
      if t[0]['name'] == 'sfb':
        sfb=[]
        tmp=[]
        head=[]
        for z in t[2]['axis']:
          head.append(z[0]['name'])
          tmp.append(map(float,z[1].split('\n')))
        for z in range(len(tmp[0])):
          try: # if errorbars in sfb area
            sfb.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                         int(tmp[head.index('kill')][z]),tmp[head.index('error')][z]])
          except:
            sfb.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                         int(tmp[head.index('kill')][z]),0.])
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

    radii=[]
    radii=os.popen('gen_rad_sfb -r '+sys.argv[-1].split('.')[0]).read().split('\n')

    sky=float(elements['sky'][0][1])
    skysig=float(elements['skysig'][0][1])
    cons=float(elements['zeropoint'][0][1])
    scale=float(elements['scale'][0][1])
  else:
    print sys.argv[-1],'XML file not found - aborting'
    sys.exit()

  try:
    for z,r in zip(sfb,radii):
      for y in ept:
        if round(y[0],2) == round(z[0],2):
          rr=float(r.split()[0])
          sfb=10.**(z[1]/-2.5)
          tot=10.**((y[1]+cons)/-2.5)
          avg=10.**((y[1]+cons)/-2.5)/(y[2]*scale*scale)
          if sfb/avg < eta:
            tot_rad=2.*interp(last_eta,sfb/avg,last_r,rr,0.20)
            raise
          last_eta=sfb/avg
          last_r=rr
  except:
    pass

  try:
    for y,r in zip(ept,radii):
      rr=float(r.split()[0])
      if rr > tot_rad:
        tot_mag=interp(last_r,rr,last_mag,y[1],tot_rad)
        break
      last_mag=y[1]
      last_r=rr

    tot_mag
    print sys.argv[-1],
    print '%.2f' % tot_rad,
    print '%.3f' % (tot_mag+cons),
    print '%.3f' % (float(elements['tot_mag_sfb'][0][1]))
  except:
    pass
