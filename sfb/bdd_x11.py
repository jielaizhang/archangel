#!/usr/bin/env python

import sys
#try:
#  import numpy.numarray as numarray
#  print 'using numpy'
#except:
#  import numarray
import numarray
from ppgplot import *
from math import *
import astropy.io.fits as pyfits
from xml_archangel import *

def errorbar(x,y,err,xmin,xmax):
  pgmove(x,y)
  pgdraw(x,y+err)
  pgdraw(x-0.01*(xmax-xmin),y+err)
  pgdraw(x+0.01*(xmax-xmin),y+err)
  pgmove(x,y)
  pgdraw(x,y-err)
  pgdraw(x-0.01*(xmax-xmin),y-err)
  pgdraw(x+0.01*(xmax-xmin),y-err)

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
  xnt = a[0] + 8.325*((x/a[1])**0.25 - 1.0)
  xnt = -0.4*xnt
  xnt1 = 10.**xnt
  xnt =  a[3] + a[2]*x
  xnt = -0.4*xnt
  xnt2 = 10.**(xnt)
  xnt3 = xnt1 + xnt2
  return -2.5*log10(xnt3)

def fchisq(s,sigmay,npts,nfree,yfit):
  chisq=0.
  for j in range(npts):
    chisq=chisq+((s[j]-yfit[j])**2)/sigmay[j]**2
  return chisq/nfree

def gridls(x,y,sigmay,npts,nterms,a,deltaa,chisqr,edge):

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

def fitx(npts,r,s,se,re,sstore,cstore,nt):

#   r,s = arrays of radius and surface brightness
#   npts = number of points
#   se = eff. surface brightness
#   re = eff. radius
#   sstore = disk scale length
#   cstore = disk surface brightness (see format below for conversion
#            to astrophysically meaningful values)
#   nt = number of parameters to fit (2 for r^1/4, 4 for B+D)
#   program would like some first guess to speed things up

  sigmay=[]
  for j in range(npts):
    sigmay.append(1.)

  nitlt=500
  if nt == 3 and sstore == 0:
#    xrint 'Disk slope required for three parameter fits'
    return 'nan','nan','nan','nan','nan'

  if se == 0: # computer guess if no input
    a=[22.,10.,3.e-2,22.]
    if nt == 2:
      a[2]=sstore
      a[3]=cstore
  else:
    a=[se,re,sstore,cstore]

  dela=[0.1,0.1,1.e-4,0.1]
  edge=[[5.,35.],[.5,5000.],[1.e-8,.5],[10.,30.]] # set edges of fit
  nit=0

#     xrint npts,r(1),r(npts)
#     xrint '              -- Initial guess --'
  alpha = 1.0857/a[2]
  xbm = a[0] - 5.*log10(a[1]) - 40.0
  xdm = a[3] - 5.*log10(alpha) - 38.6
  bdratio = 10.**(-0.4*(xbm - xdm))
#     xrint nit,bdratio,(a(i),i=1,3),alpha,chsqr

  chsqr=0.
  old=a[:]
  while (nit < nitlt):
    a,chsqr=gridls(r,s,sigmay,npts,nt,a,dela,chsqr,edge)
    if nt == 3: chsqr=chsqr*(npts-3)/(npts-4)
    nit=nit+1
    alpha = 1.0857/a[2]
    if nit > 5:
      xbm = a[0] - 5.*log10(a[1]) - 40.0
      xdm = a[3] - 5.*log10(alpha) - 38.6
      bdratio = 10.**(-0.4*(xbm - xdm))

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

  se=a[0]
  re=a[1]
  sstore=a[2]
  cstore=a[3]

  xbm = se - 5.*log10(re) - 40.0
  xdm = cstore - 5.*log10(alpha) - 38.6
  bdratio = 10.**(-0.4*(xbm - xdm))

  return chsqr,se,re,cstore,sstore

def prf_plot(data,xmin,xmax,ymin,ymax):
  r=[] ; s=[] ; v=[] ; w=[]
  for t in data:
    if t[2]:
      r.append(t[0]) ; s.append(t[1])
    else:
      v.append(t[0]) ; w.append(t[1])
  pgeras()
  pgsci(1)
  pgswin(xmin,xmax,ymin,ymax)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  pglab('r (arcsecs)','DN',sys.argv[-1].replace('.prf','').replace('.sfb',''))
  pgpt(numarray.array(r),numarray.array(s),4)
  pgpt(numarray.array(v),numarray.array(w),5)
  strng='sky ='+('%9.3g' % sky)+' +/- '+('%9.3g' % skysig)
  pgptxt(xmin+(xmax-xmin)/20.,ymax-(ymax-ymin)/20.,0.,0.,strng)
  pgsci(5)
  pgmove(xmin,sky)
  pgdraw(xmax,sky)
  pgsci(1)
  if grey: tiny_pic(xmin,xmax,ymin,ymax)

def tiny_pic(xmin,xmax,ymin,ymax):
  h1,h2,h3,h4=pgqvp(1)
  e1,e2,e3,e4=pgqvp(0)
  p1=(e2-e1)/(h2-h1)
  p2=(e4-e3)/(h4-h3)
  f2=e2-0.02*(e2-e1)
  f1=f2-0.40*(e2-e1)
  f4=e4-(p2/p1)*0.02*(e2-e1)
  if nx > ny:
    f3=f4-(p2/p1)*(nx/ny)*0.40*(e2-e1)
  else:
    f3=f4-(p2/p1)*(ny/nx)*0.40*(e2-e1)
  i1=0 ; i2=nx ; j1=0 ; j2=ny
  pgsvp(f1,f2,f3,f4)
  pgswin(i1,i2,j1,j2)
  pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
  pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
  pgsch(0.4)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  try:
    pgsci(3)
    for line in pts:
      if abs(emin)/xscale == line[3]:
        edraw(1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])
        break
    pgsvp(e1,e2,e3,e4)
    pgsch(1.0)
    if emin < 0:
      tmp=-2.5*log10((line[0]-sky)/(xscale**2))+cons
      pgswin(xmin,xmax,ymax,ymin)
    else:
      tmp=line[0]
      pgswin(xmin,xmax,ymin,ymax)
    pgpt(numarray.array([xscale*line[3]]),numarray.array([tmp]),4)
    pgsci(1)
  except:
    pgsci(1)
    pass
  pgsch(1.0)
  pgsvp(e1,e2,e3,e4)
  pgswin(xmin,xmax,ymin,ymax)

def edraw(eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  th=0.
  step=2.
  istep=int(360./step)+1
  for i in range(istep):
    th=th+step
    t=th*pi/180.
    c1=bsq*(cos(t))**2+asq*(sin(t))**2
    c2=(asq-bsq)*2*sin(t)*cos(t)
    c3=bsq*(sin(t))**2+asq*(cos(t))**2
    c4=asq*bsq
    r=(c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**.5
    if th == step:
      pgmove(r*cos(t)+xc,r*sin(t)+yc)
    else:
      pgdraw(r*cos(t)+xc,r*sin(t)+yc)
  return

def plot(data):
  pgeras()
  pgsci(1)
  r=[] ; s=[] ; v=[] ; w=[] ; e=[]
  for t in data:
    if t[2]:
      if ifit == 2:
        r.append(t[0]**0.25)
      else:
        r.append(t[0])
      s.append(t[1])
      e.append(t[3])
    else:
      if ifit == 2:
        v.append(t[0]**0.25)
      else:
        v.append(t[0])
      w.append(t[1])
  xmin=min(r+v)-0.10*(max(r+v)-min(r+v))
  ymax=max(s+w)+0.10*(max(s+w)-min(s+w))
  if ifit == 2:
    xmax=max(r+v)+0.25*(max(r+v)-min(r+v))
    ymin=min(s+w)-0.25*(max(s+w)-min(s+w))
  else:
    xmax=max(r+v)+0.10*(max(r+v)-min(r+v))
    ymin=min(s+w)-0.10*(max(s+w)-min(s+w))

  if grey:
    h1,h2,h3,h4=pgqvp(1)
    e1,e2,e3,e4=pgqvp(0)
    p1=(e2-e1)/(h2-h1)
    p2=(e4-e3)/(h4-h3)
    f2=e2-0.02*(e2-e1)
    f1=f2-0.40*(e2-e1)
    f4=e4-(p2/p1)*0.02*(e2-e1)
    if nx > ny:
      f3=f4-(p2/p1)*(nx/ny)*0.40*(e2-e1)
    else:
      f3=f4-(p2/p1)*(ny/nx)*0.40*(e2-e1)

    for i in range(10):
      b2=ymin+(f3)*(ymax-ymin)/(e4-e3)
      b1=xmax+(f1-e2)*(xmin-xmax)/(e1-e2)
      for i,t in enumerate(r):
#      print t,b1,s[r.index(t)],b2
        if t > b1 and s[i] < b2:
          xmin=xmin-0.1*xmin
#        print xmin
      for i,t in enumerate(v):
#      print t,b1,w[v.index(t)],b2
        if t > b1 and w[i] < b2:
          xmin=xmin-0.1*xmin
#        print xmin

  pgswin(xmin,xmax,ymax,ymin)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  if ifit == 2:
    pglab('r\\u1/4\\d (arcsecs)','mag',sys.argv[-1].replace('.prf','').replace('.sfb',''))
  else:
    pglab('r (arcsecs)','mag',sys.argv[-1].replace('.prf','').replace('.sfb',''))
  pgpt(numarray.array(r),numarray.array(s),4)
  n=0
  for x,y,err in zip(r,s,e):
    n+=1
    if err > abs(ymax-ymin)/200. and not n % 3: errorbar(x,y,err,xmin,xmax)
  pgpt(numarray.array(v),numarray.array(w),5)
  draw_fit(xmin,xmax,ymin,ymax)
  if grey:
    tiny_pic(xmin,xmax,ymin,ymax)
    pgswin(xmin,xmax,ymax,ymin)
    tiny_pic(xmin,xmax,ymin,ymax)

def draw_fit(xmin,xmax,ymin,ymax):
  if xmin < 0: xmin=0
  yd=(ymax-ymin)/20.
  xd=(xmax-xmin)/20.
  xstep=(xmax-xmin)/300.
  pgsls(2)

  if ifit == 2:
    if str(se) != 'nan':
      pgmove(xmin,se+8.325*((xmin**4./re)**0.25-1.))
      pgdraw(xmax,se+8.325*((xmax**4./re)**0.25-1.))
      pgsls(1)
      pgptxt(xmin+xd,ymax-3.*yd,0.,0.,'\\gm\\de\\u = '+('%5.2f' % se))
      pgptxt(xmin+xd,ymax-2.*yd,0.,0.,'r\\de\\u = '+('%5.2f' % re))
    pgsls(1)
    return

  if str(cstore) != 'nan':
    xnt=cstore+sstore*xmin
    pgmove(xmin,xnt)
    xnt=cstore+sstore*xmax
    pgdraw(xmax,xnt)
    pgptxt(xmin+xd,ymax-3.*yd,0.,0.,'\\gm\\do\\u = '+('%5.2f' % cstore))
    alpha = 1.0857/sstore
    pgptxt(xmin+xd,ymax-2.*yd,0.,0.,'\\ga = '+('%5.2f' % alpha))

  if str(re) != 'nan':
    for i in range(301):
      t=xmin+i*xstep
      xnt=se+8.325*((t/re)**0.25-1.)
      xnt=-0.4*xnt
      xnt1=10.**xnt
      if i == 0:
        pgmove(t,-2.5*log10(xnt1))
      else:
       pgdraw(t,-2.5*log10(xnt1))

  pgsls(1)

  if ifit > 2 and str(se) != 'nan':
    for i in range(301):
      t=xmin+i*xstep
      xnt=se+8.325*((t/re)**0.25-1.)
      xnt=-0.4*xnt
      xnt1=10.**xnt
      xnt=cstore+sstore*t
      xnt=-0.4*xnt
      xnt2=10.**(xnt)
      xnt3=xnt1+xnt2
      if i == 0:
        pgmove(t,-2.5*log10(xnt3))
      else:
        pgdraw(t,-2.5*log10(xnt3))
    pgptxt(xmin+xd,ymax-5.*yd,0.,0.,'\\gm\\de\\u = '+('%5.2f' % se))
    pgptxt(xmin+xd,ymax-4.*yd,0.,0.,'r\\de\\u = '+('%5.2f' % re))
    if ifit == 3:
      pgptxt(xmin+xd,ymin+yd,0.,0.,'3P Fit')
    else:
      pgptxt(xmin+xd,ymin+yd,0.,0.,'4P Fit')

    xbm = se - 5.*log10(re) - 40.0
    alpha = 1.0857/sstore
    xdm = cstore - 5.*log10(alpha) - 38.6
    bdratio = 10.**(-0.4*(xbm - xdm))
 
if __name__ == '__main__':

  if sys.argv[1] == '-h':
    print 'Usage: bdd options file_name'
    print
    print 'quick surface photometry calibration and fitting GUI'
    print
    print 'options: -h = this message'
    print '         -p = force sfb rebuild'
    print
    print 'window #1 cursor commands:'
    print 'c = contrast control   r = reset boundaries'
    print 'z = zoom on points     x = delete point'
    print 's = set sky (2 hits)   i = show that ellipse'
    print '/ = write .sfb file    q = abort'
    print
    print 'window #2 cursor commands:'
    print 'x = erase point        d = disk fit only'
    print 'm = erase all min pts  f = do bulge+disk fit'
    print 'u = erase all max pts  e = do r**1/4 fit only'
    print 'b = redo boundaries    p = toggle 3fit/4fit'
    print 'q = abort              r = reset graphics'
    print '/ = write .xml file and exit'
    sys.exit()

  if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
    doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    try:
      sky=float(elements['sky'][0][1])
    except:
      print 'sky value not found, setting to zero'
      sky=0.
    try:
      skysig=float(elements['skysig'][0][1])
    except:
      print 'skysig not found, setting to one'
      skysig=1.

    try:
      xscale=float(elements['scale'][0][1])
    except:
      print 'pixel scale value not found, setting to one'
      xscale=1.
    try:
      cons=float(elements['zeropoint'][0][1])
    except:
      print 'zeropoint not found, setting to 25.'
      cons=25.

# ifit = 1, disk only fit
#      = 2, r^1/4 only fit
#      = 3, B+D fit, hold central disk sfb
#      = 4, B+D fit, all four parameters

    ifit=3
    if sys.argv[1] != '-p':
      try:
        cstore=float(elements['mu_o'][0][1])
        sstore=1.0857/float(elements['alpha'][0][1])
      except:
        ifit=2
        cstore=float('nan')
        sstore=float('nan')
      try:
        re=float(elements['re'][0][1])
        se=float(elements['se'][0][1])
      except:
        ifit=1
        se=float('nan')
        re=float('nan')
    else:
      cstore=float('nan')
      sstore=float('nan')
      se=float('nan')
      re=float('nan')

    isfb=0
    for t in elements['array']:
      if t[0]['name'] == 'prf':
        data=[]
        pts=[]
        head=[]
        for z in t[2]['axis']:
          head.append(z[0]['name'])
          pts.append(map(float,z[1].split('\n')))
        for z in range(len(pts[0])):
          err1=pts[head.index('RMSRES')][z]/(pts[head.index('NUM')][z])**0.5
          err2=skysig/(2.)**0.5 # note sqrt(2) kluge
          data.append([pts[head.index('RAD')][z],pts[head.index('INTENS')][z],1,(err1**2+err2**2)**0.5])
        tmp=numarray.array(pts)
        pts=numarray.swapaxes(tmp,1,0)
        if sys.argv[1] == '-p': break
      if t[0]['name'] == 'sfb' and sys.argv[1] != '-p':
        isfb=1
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
    print sys.argv[-1],'XML file not found - aborting'
    sys.exit()

  pgbeg('/xs',1,1)
  pgask(0)
  pgscr(0,1.,1.,1.)
  pgscr(1,0.,0.,0.)
  pgscf(2)
  pgpap(11.0,0.8)

  grey=0
  nx=100.
  ny=100.
  for prefix in ['.fits','.fit']:
    if os.path.exists(sys.argv[-1].split('.')[0]+prefix):
      print 'reading FITS file'
      fitsobj=pyfits.open(sys.argv[-1].split('.')[0]+prefix,"readonly")
      nx=fitsobj[0].header['NAXIS1']
      ny=fitsobj[0].header['NAXIS2']
      pix=fitsobj[0].data
      fitsobj.close()
      r1=sky+50.*skysig
      r2=sky-0.05*(r1-sky)
      grey=1
      break

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

# analyze prf data to make sfb data

  if not isfb:
    while 1:

      prf_plot(data,xmin,xmax,ymin,ymax)

      d=pgband(0)

      if d[2] == 'q':
        print 'aborting'
        sys.exit()

      if d[2] == '/': break

      if d[2] == '?':
        print
        print 'c = contrast control   r = reset boundaries'
        print 'z = zoom on points     x = delete point'
        print 's = set sky (2 hits)   i = show that ellipse'
        print '/ = write .sfb file    q = abort'
        print

      if d[2] == 'c':
        rold=r1
        k=d[0]*1.5/(xmax-xmin)+0.5-1.5*xmin/(xmax-xmin)
        r1=r1*k
        if r1 < sky: r1=(rold-sky)/2.+sky
        r2=sky-0.05*r1-sky

      if d[2] == 'z':
        rmin=1.e33
        for t in data:
          r=abs(t[0]-d[0])
          if r < rmin:
            rmin=r
            y=t[1]
        ymax=y+9.*abs(y-ymin)/10.
        ymin=data[-1][1]-2.*abs(data[-1][1]-ymin)/10.
        for t in data:
          if t[1] < ymax:
            xmin=t[0]
            break

      if d[2] == 'r':
        ymin=ymin_o
        ymax=ymax_o
        xmin=xmin_o

      if d[2] == 'i':
        rmin=1.e33
        for t in data:
          r=abs(t[0]-d[0])
          if r < rmin:
            rmin=r
            emin=t[0]

      if d[2] == 'x':
        rmin=1.e33
        for i,t in enumerate(data):
          r=abs(t[0]-d[0])
          if r < rmin:
            rmin=r
            imin=i
        data[imin][2]=abs(data[imin][2]-1)

      if d[2] == 's':
        x1=d[0]
        d=pgband(0)
        x2=d[0]
        s=[]
        for t in data:
          if t[0] > x1 and t[0] < x2 and t[2]:
            s.append(t[1])
        t1,t2,e1,e2,t3,t4,t5=xits(s,3.)
        if str(e1) != 'nan':
          sky=e1
          skysig=e2

    tmp=[]
    for t in data:
      if t[1] - sky > 0: 
        err=abs(-2.5*log10((t[1]-sky)/(xscale**2))+cons- \
            (-2.5*log10((t[1]+t[3]-sky)/(xscale**2))+cons))
        tmp.append([t[0]*xscale,-2.5*log10((t[1]-sky)/(xscale**2))+cons,1,err])
    data=tmp

# do sfb fitting now

  while 1:

    plot(data)
    d=pgband(0)

# ifit = 1, disk only fit
#      = 2, r^1/4 only fit
#      = 3, B+D fit, hold central disk sfb
#      = 4, B+D fit, all four parameters

    if d[2] == 'q': sys.exit()

    if d[2] == '/':

#      file=open(sys.argv[1].replace('prf','sfb'),'w')
#      try:
#        file.write('%12.4e' % cstore)
#        file.write('%12.4e' % (1.0857/sstore))
#      except:
#        file.write('%12.4e' % 0.0)
#        file.write('%12.4e' % 0.0)
#      try:
#        file.write('%12.4e' % se)
#        file.write('%12.4e' % re)
#      except:
#        file.write('%12.4e' % 0.0)
#        file.write('%12.4e' % 0.0)
#      file.write('%12.4e' % sky)
#      file.write('%12.4e' % skysig)
#      file.write('\n')
#      for t in data:
#        file.write('%12.4e' % t[0])
#        file.write('%12.4e' % t[1])
#        file.write('%2.1i' % t[2])
#        file.write('\n')
#      file.close()

      if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
        doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
        rootNode = doc.documentElement
        elements=xml_read(rootNode).walk(rootNode)
        out=xml_write(sys.argv[-1].split('.')[0]+'.xml',rootNode.nodeName)

        try:
          for t in elements['array']:
            if t[0]['name'] == 'sfb':
              del elements['array'][elements['array'].index(t)]
          if not elements['array']: del elements['array']
        except:
          pass
        for t in ['mu_o','alpha','se','re']:
          try:
            del elements[t]
          except:
            pass

        out.loop(elements)

      else:
        out=xml_write(sys.argv[-1].split('.')[0]+'.xml','archangel')

      if str(cstore) != 'nan':
        out.dump('  <mu_o units=\'mags/arcsecs**2\'>\n    '+'%.4e' % (cstore)+'\n  </mu_o>\n')
        out.dump('  <alpha units=\'arcsecs\'>\n    '+'%.4e' % (1.0857/sstore)+'\n  </alpha>\n')

      if str(re) != 'nan':
        out.dump('  <se units=\'mags/arcsecs**2\'>\n    '+'%.4e' % (se)+'\n  </se>\n')
        out.dump('  <re units=\'arcsecs\'>\n    '+'%.4e' % (re)+'\n  </re>\n')

      out.dump('  <array name=\'sfb\'>\n')
      sfb=['radius','mu','kill','error']
      for t in sfb:
        out.dump('    <axis name=\''+t+'\'>\n')
        for line in data:
          if t == 'kill':
            out.dump('      '+'%.1i' % (line[sfb.index(t)])+'\n')
          else:
            out.dump('      '+'%.4e' % (line[sfb.index(t)])+'\n')
        out.dump('    </axis>\n')
      out.dump('  </array>\n')
      out.close()
      break

    if d[2] == '?': 
      print
      print 'x = erase point        d = disk fit only'
      print 'm = erase all min pts  f = do bulge+disk fit'
      print 'u = erase all max pts  e = do r**1/4 fit only'
      print 'b = redo boundaries    r = reset graphics'
      print '/ = write .sfb file    q = abort'
      print

    if d[2] == 'r':
      for t in data: data[data.index(t)][2]=1

    if d[2] == 'f':
      if ifit < 3: ifit=3
      r=[] ; s=[]
      for t in data:
        if t[2]:
          r.append(t[0]) ; s.append(t[1])
      if str(re) == 'nan':
        re=(1.0857/sstore)/2.
        se=cstore
      if ifit == 3:
        chisqr,se,re,cstore,sstore=fitx(len(r),r,s,se,re,sstore,cstore,2)
      else:
        chisqr,se,re,cstore,sstore=fitx(len(r),r,s,se,re,sstore,cstore,4)

    if d[2] in ['x','l','u']:
      rmin=1.e33
      for t in data:
        r=((t[0]-d[0])**2+(t[1]-d[1])**2)**0.5
        if r < rmin:
          rmin=r
          imin=data.index(t)
      if d[2] == 'x':
        data[imin][2]=abs(data[imin][2]-1)
      else:
        for t in data:
          if t[0] >= d[0] and d[2] == 'u': data[data.index(t)][2]=0
          if t[0] <= d[0] and d[2] == 'l': data[data.index(t)][2]=0

    if d[2] == 'p':
      if ifit == 3:
        ifit=4
      else:
        ifit=3

    if d[2] == 'i':
      rmin=1.e33
      for t in data:
        r=abs(t[0]-d[0])
        if r < rmin:
          rmin=r
          emin=-t[0]

    if d[2] == 'd':
      ifit=1
#      re=float('nan')
#      se=float('nan')
      plot(data)
#      d=pgband(0)
      x1=d[0]
      d=pgband(0)
      if d[2] == 'q': sys.exit()
      x2=d[0]
      fit=[]
      for t in data:
        if t[0] > x1 and t[0] < x2 and t[2]:
          fit.append([t[0],t[1],1.])
      if len(fit) > 2:
        a,b,r,sigb,sigm,sig=linfit(fit)
      else:
        print 'fit failed'
        print len(fit)
        continue
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
        if t[0] > x1 and t[0] < x2 and t[2]:
          ss=abs(perp(b,a,t[0],t[1])/sigma)
          if ss < .5: ss=.5
          fit.append([t[0],t[1],ss])
      if len(fit) > 2:
        ax,bx,rx,sigbx,sigmx,sigx=linfit(fit)
      else:
        print 'fit failed'
        continue
      sstore=bx
      cstore=ax

    if d[2] == 'e':
      ifit=2
      plot(data)
      d=pgband(0)
      x1=d[0]
      d=pgband(0)
      if d[2] == 'q': sys.exit()
      x2=d[0]
      fit=[]
      for t in data:
        if t[0]**0.25 > x1 and t[0]**0.25 < x2 and t[2]:
          fit.append([t[0]**0.25,t[1],1.])
      if len(fit) > 2:
        a,b,r,sigb,sigm,sig=linfit(fit)
      else:
        print 'fit failed'
        continue
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
        if t[0]**0.25 > x1 and t[0]**0.25 < x2 and t[2]:
          ss=abs(perp(b,a,t[0]**0.25,t[1])/sigma)
          if ss < .5: ss=.5
          fit.append([t[0]**0.25,t[1],ss])
      ax,bx,rx,sigbx,sigmx,sigx=linfit(fit)
      se=ax+8.325
      re=1./((bx/8.325)**4.)
      cstore=float('nan')
      sstore=float('nan')
