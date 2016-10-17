#!/usr/bin/env python

import sys, time
from math import *
from xml_archangel import *

if __name__ == '__main__':

  if sys.argv[1] == '-h':
    print './dump_residuals options master_file'
    print
    print 'dump residuals for all .xml files in master_file'
    print
    print 'options: -f = use master file of names'
    print '         -b = bulge+disk fit'
    print '         -e = deV fit'
    print '         -s = Sersic fit'
    sys.exit()

  if '-f' in sys.argv:
    files=[tmp[:-1] for tmp in open(sys.argv[-1],'r').readlines()]
  else:
    files=[sys.argv[-1]]

  for file in files:
    if os.path.exists(file.split('.')[0]+'.xml'):
      doc = minidom.parse(file.split('.')[0]+'.xml')
      rootNode = doc.documentElement
      elements=xml_read(rootNode).walk(rootNode)

      try:
        cstore=float(elements['mu_o'][0][1])
        sstore=1.0857/float(elements['alpha'][0][1])
        lower_fit_disk=float(elements['lower_fit_disk'][0][1])
        upper_fit_disk=float(elements['upper_fit_disk'][0][1])
        chisq_disk=float(elements['chisq_disk'][0][1])
      except:
        pass

      try:
        re_dev=float(elements['re_dev'][0][1])
        se_dev=float(elements['se_dev'][0][1])
        lower_fit_dev=float(elements['lower_fit_dev'][0][1])
        upper_fit_dev=float(elements['upper_fit_dev'][0][1])
        chisq_dev=float(elements['chisq_dev'][0][1])
      except:
        pass

      try:
        re_bulge=float(elements['re_bulge'][0][1])
        se_bulge=float(elements['se_bulge'][0][1])
        chisq_bulge=float(elements['chisq_bulge'][0][1])
      except:
        pass

      try:
        if 'auto' in sys.argv[-1]:
          re_sersic=float(file[2])
          se_sersic=float(file[1])
          n_sersic=float(file[3])
        else:
          re_sersic=float(elements['re_sersic'][0][1])
          se_sersic=float(elements['se_sersic'][0][1])
          n_sersic=float(elements['n_sersic'][0][1])
        lower_fit_sersic=float(elements['lower_fit_sersic'][0][1])
        upper_fit_sersic=float(elements['upper_fit_sersic'][0][1])
        chisq_sersic=float(elements['chisq_sersic'][0][1])
      except:
        pass

      for t in elements['array']:
        if t[0]['name'] == 'prf':
          prf=[]
          head=[]
          pts=[]
          for z in t[2]['axis']:
            head.append(z[0]['name'])
            pts.append(map(float,z[1].split('\n')))
          for z in range(len(pts[0])):
            tmp=[]
            for w in head:
              tmp.append(pts[head.index(w)][z])
            prf.append(tmp)

      for t in elements['array']:
        if t[0]['name'] == 'sfb':
          data=[]
          tmp=[]
          head=[]
          for z in t[2]['axis']:
            head.append(z[0]['name'])
            tmp.append(map(float,z[1].split('\n')))
          for z in range(len(tmp[0])):
            try: # if errorbars in sfb area
              data.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                           int(tmp[head.index('kill')][z]),tmp[head.index('error')][z]])
            except:
              data.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                           int(tmp[head.index('kill')][z]),0.])
          break
    else:
      continue

    try:
      scale=float(elements['cosmology_corrected_scale_kpc_arcsec'][0][1])
    except:
      scale=1.

    try:
      if sys.argv[1] == '-b':
        a=[se_bulge,re_bulge,sstore,cstore]
        for t in data:
          xnt = a[0] + 8.325*((t[0]/a[1])**0.25 - 1.0)
          xnt = -0.4*xnt
          xnt1 = 10.**xnt
          xnt =  a[3] + a[2]*t[0]
          xnt = -0.4*xnt
          xnt2 = 10.**(xnt)
          xnt3 = xnt1 + xnt2
          xnt3=-2.5*log10(xnt3)
          if t[2]:
            print log10(t[0]*scale),t[1]-xnt3

      if sys.argv[1] == '-e':
        a=[se_dev,re_dev]
        for t in data:
          xnt1 = a[0] + 8.325*((t[0]/a[1])**0.25 - 1.0)
          if t[2]:
            print log10(t[0]*scale),t[1]-xnt1

      if sys.argv[1] == '-s':
        a=[se_sersic,re_sersic,n_sersic]
        for t in data:
          for y in prf:
            if y[3] >= t[0]:
              tmp=(t[0]*t[0]*(1.-y[12]))**0.5
              break
          b=2.*a[2]-(1./3.)
          xnt1=-2.5*log10((10.**(a[0]/-2.5))*exp(-b*((tmp/a[1])**(1./a[2])-1.)))
          if t[2]:
            print log10(tmp),t[1]-xnt1

    except:
      pass
