#!/usr/bin/env python

import sys, os.path, pyfits, time
from math import *
from xml_archangel import *
import subprocess
from pylab import *
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Ellipse

def perp(m,b,x,y):
  if m != 0.:
    c=y+x/m
    r=(c-b)/(m+1./m)
  else:
    r=x
  s=m*r+b
  d=((r-x)**2+(s-y)**2)**0.5
  if r <= x:
    return d
  else:
    return -d

def linfit(fit):
  sum=0.0
  sumx=0.0
  sumy=0.0
  sumxy=0.0
  sumx2=0.0
  sumy2=0.0
  n=0
  for tmp in fit:
    n+=1
    sum=sum+(1./tmp[2]**2)
    sumx=sumx+(1./tmp[2]**2)*tmp[0]
    sumy=sumy+(1./tmp[2]**2)*tmp[1]
    sumxy=sumxy+(1./tmp[2]**2)*tmp[0]*tmp[1]
    sumx2=sumx2+(1./tmp[2]**2)*tmp[0]*tmp[0]
    sumy2=sumy2+(1./tmp[2]**2)*tmp[1]*tmp[1]
  dex=sum*sumx2-sumx*sumx
# y intersect -- a
  a=(sumx2*sumy-sumx*sumxy)/dex
# slope -- b
  b=(sum*sumxy-sumx*sumy)/dex
# varience
  var=(sumy2+a*a*sum+b*b*sumx2-2.*(a*sumy+b*sumxy-a*b*sumx))/(n-2)
# correlation coefficient -- r
  r=(sum*sumxy-sumx*sumy)/((dex*(sum*sumy2-sumy*sumy))**0.5)
# sigma b
  sigb=(var*sumx2/dex)**0.5
# sigma m
  sigm=(var*sum/dex)**0.5
  sig=0.
  for tmp in fit:
    z=a+b*tmp[0]
    sig=sig+(z-tmp[1])**2
  sig=(sig/(n-1))**.5
  return a,b,r,sigb,sigm,sig

def xits(x,xsig):
  xmean1=0. ; sig1=0.
  for tmp in x:
    xmean1=xmean1+tmp
  try:
    xmean1=xmean1/len(x)
  except:
    return 'nan','nan','nan','nan','nan','nan','nan'
  for tmp in x:
    sig1=sig1+(tmp-xmean1)**2
  try:
    sig1=(sig1/(len(x)-1))**0.5
  except:
    return 'nan','nan','nan','nan','nan','nan','nan'
  xmean2=xmean1 ; sig2=sig1
  xold=xmean2+0.001*sig2
  its=0
  while (xold != xmean2 and its < 100):
    xold=xmean2
    its+=1
    dum=0.
    npts=0
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        npts+=1
        dum=dum+tmp
    try:
      xmean2=dum/npts
    except:
      return xmean1,sig1,'nan','nan',len(x),'nan','nan'
    dum=0.
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        dum=dum+(tmp-xmean2)**2
    try:
      sig2=(dum/(npts-1))**0.5
    except:
      return xmean1,sig1,'nan','nan',len(x),'nan','nan'
  return xmean1,sig1,xmean2,sig2,len(x),npts,its

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

def gridls(x,y,sigmay,npts,nterms,a,deltaa,chisqr,edge):
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2

  nfree = npts - nterms
  chisqr =0.
  if nfree < 1: return

  for j in range(nterms):    # evaluate chi square at first two seach points
    yfit=[]
    for i in range(npts):
      yfit.append(airy(x[i],a))
    chisq1=fchisq(y,sigmay,npts,nfree,yfit)
    fn=0.
    delta=deltaa[j]
    a[j]=a[j]+delta

    if a[j] < edge[j][0] or a[j] > edge[j][1]:
      pass
    else:
      yfit=[]
      for i in range(npts):
        yfit.append(airy(x[i],a))
      chisq2=fchisq(y,sigmay,npts,nfree,yfit)
      chisq3=0.

      if chisq1-chisq2 < 0:  # reverse direction of search if chi square is increasing
        delta=-delta
        a[j]=a[j]+delta
        yfit=[]
        for i in range(npts):
          yfit.append(airy(x[i],a))
        save=chisq1
        chisq1=chisq2
        chisq2=save

      while (1):
        fn=fn+1.0            # increment a(j) until chi square increases
        a[j]=a[j]+delta
        if a[j] < edge[j][0] or a[j] > edge[j][1]: break
        yfit=[]
        for i in range(npts):
          yfit.append(airy(x[i],a))
        chisq3=fchisq(y,sigmay,npts,nfree,yfit)
        if chisq3-chisq2 >= 0: break
        chisq1 = chisq2
        chisq2 = chisq3
        if fn > 1000.: break

      fix=chisq3-chisq2    # find minimum of parpbola defined by last three points
      if fix == 0: fix=1.e-8
      delta=delta*(1./(1.+(chisq1-chisq2)/fix)+0.5)
      fix=nfree*(chisq3-2.*chisq2+chisq1)
      if fix == 0: fix=1.e-8

    a[j]=a[j]-delta
    deltaa[j]=deltaa[j]*fn/3.

  yfit=[]              # evaluate fit an chi square for final parameters
  for i in range(npts):
    yfit.append(airy(x[i],a))
  chisqr=fchisq(y,sigmay,npts,nfree,yfit)
  return a,chisqr

def fit_sersic(npts,r,s,se_sersic,re_sersic,n_sersic,sigmay):

#   r,s = arrays of radius and surface brightness
#   npts = number of points
#   se = eff. surface brightness
#   re = eff. radius
#   ns = secsic index
#   program would like some first guess to speed things up

  nitlt=500

  if str(se_sersic) == 'nan': # computer guess if no input
    a=[22.,10.,3.]
  else:
    a=[se_sersic,re_sersic,n_sersic]

  dela=[0.1,0.1,0.1,]
  edge=[[5.,35.],[.5,5000.],[0.1,20.]] # set edges of fit
  nit=0

  chsqr=0. ; old_chi=1.e33
  old=a[:]
  if '-v' in sys.argv: print 'start search',a
  while (nit < nitlt):
    if npts == 0: break
    try:
      if '-v' in sys.argv: print 'start grid'
      a,chsqr=gridls(r,s,sigmay,npts,3,a,dela,chsqr,edge)
      if '-v' in sys.argv: print 'stop grid',a,chsqr
    except:
      print 'it fail'
      print 'it#',nit,a,npts
      raise
    nit=nit+1
    if '-v' in sys.argv: print 'it',nit,a
    dif1=abs(a[0]-old[0]) # compare to old fit for convergence test
    dif2=abs(a[1]-old[1])
    dif3=abs(a[2]-old[2])
    dif=dif1+dif2+dif3
#    if (dif < 1e-7) and (nit > 50): break
    if '-v' in sys.argv: print nit,abs((old_chi-chsqr)/chsqr)
    if abs((old_chi-chsqr)/chsqr) < 1.e-7 and (nit > 50): break
    old=a[:]
    old_chi=chsqr

  se_sersic=a[0]
  re_sersic=a[1]
  n_sersic=a[2]

  return chsqr,se_sersic,re_sersic,n_sersic

def fitx(npts,r,s,nt):
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2

# fit bulge and disk
#   r,s = arrays of radius and surface brightness
#   npts = number of points
#   se = eff. surface brightness
#   re = eff. radius
#   sstore = disk scale length
#   cstore = disk surface brightness (see format below for conversion
#            to astrophysically meaningful values)
#   nt = number of parameters to fit (3 for fixed central sfb, 4 for full B+D)
#   program would like some first guess to speed things up

  sigmay=[]
  for j in range(npts):
    sigmay.append(1.)

  nitlt=500
#  if nt == 3 and sstore == 0:
#    print 'Disk slope required for three parameter fits'
#    return 'nan','nan','nan','nan','nan'

  if ifit == 3:
    a=[22.,10.,cstore]
    dela=[0.1,0.1,0.1]
    edge=[[5.,35.],[.5,5000.],[10.,30.]] # set edges of fit

  else:
    if str(se_bulge) == 'nan': # computer guess if no input
      a=[22.,10.,3.e-2,22.]
      if nt == 3:
        a[2]=sstore
        a[3]=cstore
    else:
      a=[se_bulge,re_bulge,sstore,cstore]

    dela=[0.1,0.1,1.e-4,0.1]
    edge=[[5.,35.],[.5,5000.],[1.e-8,.5],[10.,30.]] # set edges of fit

  nit=0

#  print npts,r(1),r(npts)
#  print '              -- Initial guess --'

  alpha=1.0857/a[2]
  chsqr=0.
  old=a[:]
  while (nit < nitlt):
    a,chsqr=gridls(r,s,sigmay,npts,nt,a,dela,chsqr,edge)
    if nt == 3: chsqr=chsqr*(npts-3)/(npts-4)
    nit=nit+1

    dif1=abs(a[0]-old[0]) # compare to old fit for convergence test
    dif2=abs(a[1]-old[1])
    dif3=abs(a[2]-old[2])
    dif=dif1+dif2+dif3
    if nt == 4:
      dif=(dif+10.*abs(a[3]-old[3]))/4
    else:
      dif=dif/3
    if (dif < 1e-7) and (nit > 50): break
    old=a[:]

#      if(mod(nit,20).eq.0: # ever 20th step - reset step size
#         dela(1)=0.1
#         dela(2)=0.1
#         dela(3)=0.1
#         dela(4)=1.e-4

  if ifit == 3:
    se_bulge=a[0]
    re_bulge=a[1]
    cstore=a[2]
  else:
    se_bulge=a[0]
    re_bulge=a[1]
    sstore=a[2]
    cstore=a[3]

  alpha = 1.0857/sstore
  xbm = se_bulge - 5.*log10(re_bulge) - 40.0
  xdm = cstore - 5.*log10(alpha) - 38.6
  bdratio = 10.**(-0.4*(xbm - xdm))

  return chsqr,se_bulge,re_bulge,cstore,sstore

def help():
  return '''
Usage: ./auto_fit options file_name

do command line fit

options: -h = this message
         -b = 3parm B+D fit (untested)
         -p = 4parm B+D fit (untested)
         -e = r^1/4 fit (untested)
         -s = Sersic mode
         -x = xmin,xmax fit range
        -mu = use lower sfb cutoff
       -sig = use real errors
         -d = display new fit and xml fit
'''
  return

if __name__ == '__main__':

# runtime warnings
  import warnings
  warnings.filterwarnings('ignore')

  if sys.argv[1] == '-h':
    print help()
    sys.exit()

  x1=x2=cstore=sstore=re_bulge=se_bulge=re_dev=se_dev=re_sersic=se_sersic=n_sersic='nan'
  ifit=0

  if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
    doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    try:
      sky=float(elements['sky'][0][1])
    except:
      sky=0.
    try:
      skysig=float(elements['skysig'][0][1])
    except:
      skysig=1.

    try:
      xscale=float(elements['scale'][0][1])
    except:
      xscale=1.
    try:
      cons=float(elements['zeropoint'][0][1])
    except:
      cons=25.

    try:
      k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05,'1563':0.10,'1564':0.10,'1565':0.10,'1566':0.10,'1391':0.10,'1494':0.10}
      exptime=float(elements['exptime'][0][1])
      if exptime != 0: # exptime = 0. signals all calibration in zeropoint, no airmass
        airmass=float(elements['airmass'][0][1])
        cons=2.5*log10(exptime)+cons
        cons=cons-k[elements['filter'][0][1]]*airmass
    except:
      pass
#      print 'failed to find airmass or exptime or filter'

# ifit = 1, disk only fit
#      = 2, r^1/4 only fit
#      = 3, B+D fit, hold central disk sfb
#      = 4, B+D fit, all four parameters
#      = 5, Sersic fit

    try:
      cstore=float(elements['mu_o'][0][1])
      sstore=1.0857/float(elements['alpha'][0][1])
      x1=lower_fit_disk=float(elements['lower_fit_disk'][0][1])
      x2=upper_fit_disk=float(elements['upper_fit_disk'][0][1])
      chisq_disk=float(elements['chisq_disk'][0][1])
      ifit=1
    except:
      pass

    try:
      re_dev=float(elements['re_dev'][0][1])
      se_dev=float(elements['se_dev'][0][1])
      lower_fit_dev=float(elements['lower_fit_dev'][0][1])
      upper_fit_dev=float(elements['upper_fit_dev'][0][1])
      chisq_dev=float(elements['chisq_dev'][0][1])
      ifit=2
    except:
      pass

    try:
      re_bulge=float(elements['re_bulge'][0][1])
      se_bulge=float(elements['se_bulge'][0][1])
      chisq_bulge=float(elements['chisq_bulge'][0][1])
      ifit=3
    except:
      pass

    try:
      re_sersic=float(elements['re_sersic'][0][1])
      se_sersic=float(elements['se_sersic'][0][1])
      n_sersic=float(elements['n_sersic'][0][1])
      lower_fit_sersic=float(elements['lower_fit_sersic'][0][1])
      upper_fit_sersic=float(elements['upper_fit_sersic'][0][1])
      chisq_sersic=float(elements['chisq_sersic'][0][1])
      ifit=5
    except:
      pass

    try:
      origin=elements['origin'][0][1]
    except:
      origin=None

    if '-err' in sys.argv:
      m=sys.argv.index('-err')
      err_sfb=float(sys.argv[m+1])

    if '-e' in sys.argv:
      ifit=2
      x1=lower_fit_dev**0.25
      x2=upper_fit_dev**0.25
    elif '-s' in sys.argv:
      ifit=5
      x1=log10(lower_fit_sersic)
      x2=log10(upper_fit_sersic)

    isfb=0
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
          if origin == '2MASS' and tmp[head.index('radius')][z] < 2.:
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

    if x1 != x1: x1=data[0][0]
    if x2 != x2: x2=data[-1][0]

  else:
    print sys.argv[-1],'XML file not found - aborting'
    sys.exit()

  r=[] ; s=[]
  for t in data:
    if t[2]:
      r.append(t[0])
      s.append(t[1])
  xmin=min(r)-0.10*(max(r)-min(r))
  xmax=max(r)+0.10*(max(r)-min(r))
  ymin=min(s)-0.10*(max(s)-min(s))
  ymax=max(s)+0.10*(max(s)-min(s))
  ymin_o=ymin ; ymax_o=ymax ; xmin_o=xmin

  if '-e' in sys.argv:
    try:
      x1=lower_fit_dev**0.25
      x2=upper_fit_dev**0.25
    except:
      for t in data:
        if t[2]:
          x1=t[0]**0.25
          break
      x2=data[-1][0]**0.25
    last_x1=x1 ; last_x2=x2
    ifit=2

  if '-b' in sys.argv:
    ifit=3

  if '-s' in sys.argv:
    try:
      x1=log10(lower_fit_sersic)
      x2=log10(upper_fit_sersic)
    except:
      for t in data:
        if t[2]:
          x1=log10(t[0])
          break
      for t in data:
        if t[3] > 0.5:
          x2=log10(t[0])
          break
    last_x1=x1 ; last_x2=x2
    ifit=5

  if '-p' in sys.argv:
    ifit=4

  mu_lower=35.
  if '-mu' in sys.argv:
    m=sys.argv.index('-mu')
    mu_lower=float(sys.argv[m+1])

  if '-x' in sys.argv:
    m=sys.argv.index('-x')
    x1=float(sys.argv[m+1])
    x2=float(sys.argv[m+2])
    if '-e' in sys.argv:
      x1=x1**0.25
      x2=x2**0.25
    if '-s' in sys.argv:
      x1=log10(x1)
      x2=log10(x2)

  fit=[]
  if ifit == 1 or ifit == 6:
    for t in data:
      if t[0] > x1 and t[0] < x2 and t[2]:
        fit.append([t[0],t[1],1.])
    if len(fit) > 2:
      a,b,r,sigb,sigm,sig=linfit(fit)
    try:
      xmean=0.
      sig=[]
      for t in fit:
        if t[0] > x1 and t[0] < x2 and t[2]:
          xmean=xmean+perp(b,a,t[0],t[1])
          sig.append(perp(b,a,t[0],t[1]))
      xmean=xmean/len(sig)
      sigma=0.
      for tmp in sig:
        sigma=sigma+(xmean-tmp)**2
      sigma=(sigma/(len(sig)-1.))**0.5
    except:
      pass
    fit=[]
    for t in data:
      if t[0] > x1 and t[0] < x2 and t[2]:
        ss=abs(perp(b,a,t[0],t[1])/sigma)
        if ss < .5: ss=.5
        fit.append([t[0],t[1],ss])
    if len(fit) > 2:
      ax,bx,rx,sigbx,sigmx,sigx=linfit(fit)
    try:
      sstore=bx
      cstore=ax
      s=[] ; sigmay=[] ; yfit=[] ; npts=0 ; nfree=2
      for z in fit:
        npts=npts+1
        s.append(z[1])
        sigmay.append(1.)
        yfit.append(bx*z[0]+ax)
      chisq_disk=fchisq(s,sigmay,npts,nfree,yfit)
    except:
      pass

  if ifit == 2:
    for t in data:
       for y in prf:
         if y[3] >= t[0]:
           tmp=(t[0]*t[0]*(1.-y[12]))**0.5
           if tmp**0.25 > x1 and tmp**0.25 < x2 and t[2]:
             fit.append([tmp**0.25,t[1],1.])
           break

    if len(fit) > 2:
      a,b,r,sigb,sigm,sig=linfit(fit)
    xmean=0.
    sig=[]
    for t in fit:
      if t[0] > x1 and t[0] < x2 and t[2]:
        xmean=xmean+perp(b,a,t[0],t[1])
        sig.append(perp(b,a,t[0],t[1]))
    xmean=xmean/len(sig)
    sigma=0.
    for tmp in sig:
      sigma=sigma+(xmean-tmp)**2
    sigma=(sigma/(len(sig)-1.))**0.5
    fit=[]
    for t in data:
       for y in prf:
         if y[3] >= t[0]:
           tmp=(t[0]*t[0]*(1.-y[12]))**0.5
           if tmp**0.25 > x1 and tmp**0.25 < x2 and t[2]:
             ss=abs(perp(b,a,tmp**0.25,t[1])/sigma)
             if ss < .5: ss=.5
             fit.append([tmp**0.25,t[1],ss])
    ax,bx,rx,sigbx,sigmx,sigx=linfit(fit)
    se_dev=ax+8.325
    re_dev=1./((bx/8.325)**4.)
    s=[] ; sigmay=[] ; yfit=[] ; npts=0 ; nfree=2
    for z in fit:
      npts=npts+1
      s.append(z[1])
      sigmay.append(1.)
      yfit.append(bx*z[0]+ax)
    chisq_dev=fchisq(s,sigmay,npts,nfree,yfit)
        
  if ifit in [3,4]:
    r=[] ; s=[]
    for t in data:
      if t[2]:
        r.append(t[0])
        s.append(t[1])

    if ifit == 3:
      if str(re_bulge) == 'nan':
        re_bulge=(1.0857/sstore)/2.
        se_bulge=cstore
      chisq_bulge,se_bulge,re_bulge,cstore,sstore=fitx(len(r),r,s,3)
    else:
        chisq_bulge,se_bulge,re_bulge,cstore,sstore=fitx(len(r),r,s,4)

  if ifit == 5:
    r=[] ; s=[] ; sigmay=[]
    for t in data:
      for y in prf:
        if y[3] >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          if log10(tmp) > x1 and log10(tmp) < x2 and t[1] < mu_lower and t[2]:
            r.append(tmp) ; s.append(t[1])
            if '-sig' in sys.argv:
              sigmay.append(t[-1])
            else:
              sigmay.append(1.)
          break

    if '-v' in sys.argv: print 'begin fit',len(r),se_sersic,re_sersic,n_sersic
    chisq_sersic,se_sersic,re_sersic,n_sersic=fit_sersic(len(r),r,s,se_sersic,re_sersic,n_sersic,sigmay)
    print sys.argv[-1],
    print 3*'%.2f ' % (se_sersic,re_sersic,n_sersic),
    print '%.2e' % chisq_sersic
    if '-d' in sys.argv:
      os.system('compare_sersic '+elements['se_sersic'][0][1]+' '+elements['re_sersic'][0][1]+' '+ \
                elements['n_sersic'][0][1]+' '+str(se_sersic)+' '+str(re_sersic)+' '+str(n_sersic)+' '+sys.argv[-1])

