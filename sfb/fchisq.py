#!/usr/bin/env python

import sys, os.path, time, numpy
import astropy.io.fits as pyfits
from math import *
from xml_archangel import *
import subprocess
from pylab import *
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Ellipse

def airy(x,a):
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2

  if ifit == 3: # r^1/4 bulge + exp disk fit, hold alpha
    xnt = a[0] + 8.325*((x/a[1])**0.25 - 1.0)
    xnt = -0.4*xnt
    xnt1 = 10.**xnt
    xnt =  a[2] + sstore*x
    xnt = -0.4*xnt
    xnt2 = 10.**(xnt)
    xnt3 = xnt1 + xnt2
    return -2.5*log10(xnt3)
  elif ifit == 4: # r^1/4 bulge + exp disk fit
    xnt = a[0] + 8.325*((x/a[1])**0.25 - 1.0)
    xnt = -0.4*xnt
    xnt1 = 10.**xnt
    xnt =  a[3] + a[2]*x
    xnt = -0.4*xnt
    xnt2 = 10.**(xnt)
    xnt3 = xnt1 + xnt2
    return -2.5*log10(xnt3)
  elif ifit == 5: # Sersic fit
    b=1.9992*a[2]-0.3271
    return a[0]+(2.5*b)*((x/a[1])**(1./a[2])-1.)/log(10.)

def fchisq(s,sigmay,npts,nfree,yfit):
  chisq=0.
  for j in range(npts):
    chisq=chisq+((s[j]-yfit[j])**2)/sigmay[j]**2
  return chisq/nfree

if __name__ == '__main__':

# runtime warnings
  import warnings
  warnings.filterwarnings('ignore')

  if '-h' in sys.argv:
    print './fchisqr gal_prefix'
    print
    print 'determines reduced chi^2 for stored sersic fit (output log10)'
    print
    print 'options: -s = set all errors to 1'
    sys.exit()

  if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
    doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    try:
      sky=float(elements['sky'][0][1])
      skysig=float(elements['skysig'][0][1])
      re_sersic=float(elements['re_sersic'][0][1])
      se_sersic=float(elements['se_sersic'][0][1])
      n_sersic=float(elements['n_sersic'][0][1])
      lower_fit_sersic=float(elements['lower_fit_sersic'][0][1])
      upper_fit_sersic=float(elements['upper_fit_sersic'][0][1])
      chisq_sersic=float(elements['chisq_sersic'][0][1])
      ifit=5
    except:
      pass

    for t in elements['array']:
      if t[0]['name'] == 'prf':
        prf=[]
        data=[]
        head=[]
        for z in t[2]['axis']:
          prf.append(map(float,z[1].split('\n')))
          head.append(z[0]['name'])
        for z in range(len(prf[0])):
          err1=prf[head.index('RMSRES')][z]/(prf[head.index('NUM')][z])**0.5
          err2=skysig/(2.)**0.5 # note sqrt(2) kluge
          data.append([prf[head.index('RAD')][z],prf[head.index('INTENS')][z],1,(err1**2+err2**2)**0.5])
        tmp=array(prf)
        prf=swapaxes(tmp,1,0)
        if sys.argv[1] == '-p': break

    for t in elements['array']:
      if t[0]['name'] == 'sfb' and sys.argv[1] != '-p':
        isfb=1
        data=[]
        tmp=[]
        head=[]
        for z in t[2]['axis']:
          head.append(z[0]['name'])
          tmp.append(map(float,z[1].split('\n')))
        for z in range(len(tmp[0])):
          if tmp[head.index('radius')][z] < 2.:
            kill=0
          else:
            kill=int(tmp[head.index('kill')][z])
          try: # if errorbars in sfb area
            data.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                         kill,tmp[head.index('error')][z]])
          except:
            data.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                         kill,0.])
        break

  last_x1=lower_fit_sersic ; last_x2=upper_fit_sersic

  r=[] ; s=[] ; sigmay=[] ; yfit=[]
  a=[se_sersic,re_sersic,n_sersic]
  for t in data:
    for y in prf:
      if y[3] >= t[0]:
        tmp=(t[0]*t[0]*(1.-y[12]))**0.5
        if tmp > lower_fit_sersic and tmp < upper_fit_sersic and t[2]:
          r.append(tmp) ; s.append(t[1])
          if '-s' in sys.argv:
            sigmay.append(1.)
          else
            sigmay.append(t[-1])
        break

  for i in range(len(r)):
    yfit.append(airy(r[i],a))
  print log10(fchisq(s,sigmay,len(r),len(r)-3,yfit))

