#!/usr/bin/env python

import sys, math
from xml_archangel import *

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

if __name__ == '__main__':

  if sys.argv[1] == '-h':
    print 'calculate petrosian values, needs .xml file'
    sys.exit()

#  print sys.argv[1],

  if os.path.exists(sys.argv[1].split('.')[0]+'.xml'):
    doc = minidom.parse(sys.argv[1].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

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
    print sys.argv[1],'XML file not found - aborting'
    sys.exit()

  try:
    elements['tot_mag_iter_pt'][0][1]
  except:
    print 'no iter point'
    sys.exit()

  for imin,y in enumerate(ept):
    if round(y[0],2) == float(elements['tot_mag_iter_pt'][0][1]): break

  xlum=10.**((ept[imin][1])/-2.5)
  last=[1.,0.,ept[0][1]]
  isw=0
  for z in sfb:
    for n,y in enumerate(ept):
      if round(y[0],2) == round(z[0],2):
        sfb=10.**(z[1]/-2.5)
        tot=10.**((y[1]+cons)/-2.5)
        avg1=10.**((y[1]+cons)/-2.5)/(y[2]*scale*scale)
        if n >= imin:
          xlum=xlum+10.**(y[4]/-2.5)
          tmp=-2.5*math.log10(xlum)+cons
          avg2=10.**((tmp)/-2.5)/(y[2]*scale*scale)
        else:
          tmp=y[1]
          avg2=avg1
        if sys.argv[-1] == sys.argv[1]:
          print '%.2f' % (z[0]*scale),
          print '%.3f' % (sfb/avg1),'%.3f' % y[1],
          print '%.3f' % (sfb/avg2),'%.3f' % (tmp-cons)
        else:
          if sfb/avg1 < float(sys.argv[-1]):
            isw=1
            print '%.2f' % interp(last[0],sfb/avg1,last[1],z[0]*scale,float(sys.argv[-1])),
            print '%.3f' % interp(last[0],sfb/avg1,last[2],y[1],float(sys.argv[-1])),
            print '%.3f' % interp(last[0],sfb/avg1,last[2]+cons,y[1]+cons,float(sys.argv[-1])),
            try:
              print elements['tot_mag_sfb'][0][1],
              print elements['tot_mag_quality'][0][1]
            except:
              print 'None fail'
            sys.exit()
        break
    try:
      last=[sfb/avg1,z[0]*scale,y[1]]
    except:
      last=[1.,z[0]*scale,y[1]]

  if not isw: print 'petrosian value not found, fail'
