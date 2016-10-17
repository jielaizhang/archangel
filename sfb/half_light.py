#!/usr/bin/env python

import sys
from xml_archangel import *

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

if __name__ == '__main__':

  if sys.argv[1] == '-h':
    print 'calculate petrosian value for its half light radius'
    sys.exit()

  if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
    doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
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

    sky=float(elements['sky'][0][1])
    skysig=float(elements['skysig'][0][1])
    cons=float(elements['zeropoint'][0][1])
    scale=float(elements['scale'][0][1])
  else:
    print sys.argv[-1],'XML file not found - aborting'
    sys.exit()

  for n,z in enumerate(sfb):
    if z[0] > half:
      sfb_half=interp(sfb[n-1][0],sfb[n][0],sfb[n-1][1],sfb[n][1],half)
      for m,y in enumerate(ept):
        if y[0] > half:
          tot_half=interp(ept[m-1][0],ept[m][0],ept[m-1][1],ept[m][1],half)
          area_half=interp(ept[m-1][0],ept[m][0],ept[m-1][2],ept[m][2],half)
          t1=10.**(sfb_half/-2.5)
          t2=10.**((tot_half+cons)/-2.5)/(area_half*scale*scale)
          print t1/t2,sfb_half,sys.argv[-1]
          sys.exit()

  print 'fail',sys.argv[-1]
