#!/usr/bin/env python

import sys, os.path, time
import astropy.io.fits as pyfits
from math import *
from xml_archangel import *
import subprocess

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

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
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2,origin

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
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2,origin

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

def fit_sersic(npts,r,s,se_sersic,re_sersic,n_sersic):

#   r,s = arrays of radius and surface brightness
#   npts = number of points
#   se = eff. surface brightness
#   re = eff. radius
#   ns = secsic index
#   program would like some first guess to speed things up

  sigmay=[]
  for j in range(npts):
    sigmay.append(1.)

  nitlt=500

  if str(se_sersic) == 'nan': # computer guess if no input
    a=[22.,10.,1.]
  else:
    a=[18.,2.,1.]
#    a=[se_sersic,re_sersic,n_sersic]

  dela=[0.1,0.1,0.1,]
  edge=[[5.,35.],[.5,5000.],[0.1,15.]] # set edges of fit
  nit=0

  chsqr=0. ; old_chi=1.e33
  old=a[:]
  while (nit < nitlt):
    if npts == 0: break
    try:
      a,chsqr=gridls(r,s,sigmay,npts,3,a,dela,chsqr,edge)
    except:
      print 'it fail'
      print 'it#',nit,a,npts
    nit=nit+1
    dif1=abs(a[0]-old[0]) # compare to old fit for convergence test
    dif2=abs(a[1]-old[1])
    dif3=abs(a[2]-old[2])
    dif=dif1+dif2+dif3
#    if (dif < 1e-7) and (nit > 50): break
    if abs((old_chi-chsqr)/chsqr) < 1.e-7 and (nit > 50): break
    old_chi=chsqr
    old=a[:]

  se_sersic=a[0]
  re_sersic=a[1]
  n_sersic=a[2]

  return chsqr,se_sersic,re_sersic,n_sersic

def fitx(npts,r,s,nt):
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2,origin

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

def auto_sfb():
  global ax,isfb,data,xmin,xmax,ymin,ymax,switch,sky,skysig,osky,pix,r1,r2,prf,emin,s1,s2,errsig
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2,origin
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic 
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge

  tmp=[]
  ierr=0
  for t in data:
    if t[1] - sky > 0 and t[2]: 
      err=abs(-2.5*log10((t[1]-sky)/(xscale**2))+cons- \
          (-2.5*log10((t[1]+t[3]-sky)/(xscale**2))+cons))
      if origin == '2MASS' and t[0]*xscale < 5.:
        tmp.append([t[0]*xscale,-2.5*log10((t[1]-sky)/(xscale**2))+cons,0,err])
      else:
        if (errsig > 0. and err > errsig) or ierr:
          ierr=1
          tmp.append([t[0]*xscale,-2.5*log10((t[1]-sky)/(xscale**2))+cons,0,err])
        else:
          tmp.append([t[0]*xscale,-2.5*log10((t[1]-sky)/(xscale**2))+cons,1,err])
  data=tmp
  return

def prf_plot(): # display the raw intensity DN
  global ax,isfb,data,xmin,xmax,ymin,ymax,switch,sky,skysig,osky,pix,r1,r2,prf,emin,s1,s2,errsig
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2,origin
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic 
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge

  axis([xmin,xmax,ymin,ymax])
  xlabel('r (arcsecs)')
  ylabel('DN')
  suptitle(sys.argv[-1].split('.')[0])

  strng='sky = '+('%.3g' % sky)+' +/- '+('%.3g' % skysig)
  text(xmin+(xmax-xmin)/10.,ymax-(ymax-ymin)/20.,strng,horizontalalignment='left',verticalalignment='center')
  ax.plot([xmin,xmax],[osky,osky],'r--')
  ax.plot([xmin,xmax],[sky,sky],'b-')
  try:
    text(s1,sky-0.03*(ymax-ymin),'$\uparrow$',color='g', \
         horizontalalignment='center',verticalalignment='center')
    text(s2,sky-0.03*(ymax-ymin),'$\uparrow$',color='g', \
         horizontalalignment='center',verticalalignment='center')
  except:
    pass

  try:
    for t in prf:
      if round(t[3],2) == round(emin,2):
        ax.scatter([t[3]],[t[0]],s=200,marker='o',color='g',facecolor='w')
        break
  except:
    pass

  r=[] ; s=[] ; v=[] ; w=[]
  for t in data:
    if t[2]:
      r.append(t[0]) ; s.append(t[1])
    else:
      v.append(t[0]) ; w.append(t[1])
  ax.scatter(r,s,s=75,marker=(4,0,0),color='k')
  if len(v) > 0: 
    ax.scatter(v,w,s=75,marker='x',color='r')
  ax.set_xlim(xmin,xmax)
  ax.set_ylim(ymin,ymax)

  if grey:
    a = axes([.50,.50,.35,.35])
    ticklabels = a.get_xticklabels()
    for label in ticklabels:
      label.set_fontsize(9)
    ticklabels = a.get_yticklabels()
    for label in ticklabels:
      label.set_fontsize(9)
#    setp(a,xticks=[],yticks=[])
    gray()
    imshow(-pix,vmin=-r1,vmax=-r2,aspect='equal',origin='lower',interpolation='nearest')
    try:
      for t in prf:
        if round(t[3],2) == round(emin,2):
          e=Ellipse((t[14],t[15]),2.*t[3],2.*t[3]*(1.-t[12]),t[13],fill=0)
          break
      e.set_clip_box(a.bbox)
      e.set_alpha(1.0)
      e.set_edgecolor('g')
      a.add_artist(e)
    except:
      pass

  draw()
  return

def plot_bdd():
  global ax,isfb,data,xmin,xmax,ymin,ymax,switch,sky,skysig,osky,pix,r1,r2,prf,emin,s1,s2,errsig
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2,origin
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic 
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge

#  ioff() # hold drawing until everything is done
  r=[] ; s=[] ; v=[] ; w=[] ; e=[]
  for i,t in enumerate(data):
    for y in prf:
      if y[3] >= t[0]:
        tmp=(t[0]*t[0]*(1.-y[12]))**0.5
        break
    else:
      tmp=(t[0]*t[0]*(1.-y[12]))**0.5
    if t[2]:
      if ifit == 2:
        r.append(tmp**0.25)
      elif ifit == 5:
        r.append(log10(tmp))
      else:
        r.append(t[0])
      s.append(t[1])
      e.append(t[3])
    else:
      if ifit == 2:
        v.append(tmp**0.25)
      elif ifit == 5:
        v.append(log10(tmp))
      else:
        v.append(t[0])
      w.append(t[1])

# set limits, check for data inside image frame
#  xmin=min(r+v)-0.10*(max(r+v)-min(r+v))
#  xmax=max(r+v)+0.10*(max(r+v)-min(r+v))
#  ymin=min(s+w)-0.10*(max(s+w)-min(s+w))
#  ymax=max(s+w)+0.10*(max(s+w)-min(s+w))
  xmin=min(r)-0.10*(max(r)-min(r))
  xmax=max(r)+0.10*(max(r)-min(r))
  ymin=min(s)-0.10*(max(s)-min(s))
  ymax=max(s)+0.10*(max(s)-min(s))
  if origin == 'SDSS':
    ymin=14. ; ymax=30.
  if ifit == 6: xmax=2.*x2
  isw=1
  while (isw):
    isw=0
    for t in data:
      if ifit == 2:
        t1=t[0]**0.25
      elif ifit == 5:
        t1=log10(t[0])
      else:
        t1=t[0]
      if t1 > xmin+(xmax-xmin)/2.2 and t[1] < ymax-(ymax-ymin)/2.2:
        isw=1
        xmax=xmax+0.10*(xmax-xmin)
        ymin=ymin-0.10*(ymax-ymin)

  axis([xmin,xmax,ymax,ymin])
  if ifit == 2:
    xlabel('((a*b)$^{1/2}$)$^{1/4}$ (arcsecs)')
  elif ifit == 5:
    xlabel('log (a*b)$^{1/2}$ (arcsecs)')
  else:
    xlabel('r (arcsecs)')
  ylabel('mag/arcsec$^{-2}$')
  suptitle(sys.argv[-1].split('.')[0])

  try:
    for t in data:
      for y in prf:
        if y[3] >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          break
      if round(t[0],2) == round(emin,2):
        if ifit == 2:
          ax.scatter([tmp**0.25],[t[1]],s=200,marker='o',color='g',facecolor='w')
        elif ifit == 5:
          ax.scatter([log10(tmp)],[t[1]],s=200,marker='o',color='g',facecolor='w')
        else:
          ax.scatter([t[0]],[t[1]],s=200,marker='o',color='g',facecolor='w')
        break
  except:
    pass

# facecolor to give open symbols
  ax.scatter(r,s,s=75,marker=(4,0,0),facecolor=(1,1,1,0),color='k')
  if len(v) > 0:
    ax.scatter(v,w,s=75,marker='x',color='r')
  ax.set_xlim(xmin,xmax)
  ax.set_ylim(ymax,ymin)

  try:
    if str(x1) != 'nan' or str(x2) != 'nan':
      for t in data:
        if ifit == 2:
          t1=t[0]**0.25
        elif ifit == 5:
          t1=log10(t[0])
        else:
          t1=t[0]
        if t1 > x1: break
        lastx=t1
        lasty=t[1]
      try:
        text(x1,lasty+(x1-lastx)*(t[1]-lasty)/(t1-lastx)+0.03*(ymax-ymin),'$\uparrow$',color='g', \
             horizontalalignment='center',verticalalignment='center')
      except:
        text(x1,t[1]+0.03*(ymax-ymin),'$\uparrow$',color='g', \
             horizontalalignment='center',verticalalignment='center')
      for t in data:
        if ifit == 2:
          t1=t[0]**0.25
        elif ifit == 5:
          t1=log10(t[0])
        else:
          t1=t[0]
        if t1 > x2: break
        lastx=t1
        lasty=t[1]
      if lasty+(x2-lastx)*(t[1]-lasty)/(t1-lastx)+0.03*(ymax-ymin) < ymax:
        text(x2,lasty+(x2-lastx)*(t[1]-lasty)/(t1-lastx)+0.03*(ymax-ymin),'$\uparrow$',color='g', \
             horizontalalignment='center',verticalalignment='center')
      else:
        text(x2,ymax-0.03*(ymax-ymin),'$\uparrow$',color='g', \
             horizontalalignment='center',verticalalignment='center')
  except:
    pass

  n=0
  for x,y,err in zip(r,s,e):
    n+=1
    if err > abs(ymax-ymin)/200. and err > .1: errorbar(x,y,yerr=err,ecolor='k')

  draw_fit()

  if grey:
    a = axes([.50,.50,.35,.35])
    ticklabels = a.get_xticklabels()
    for label in ticklabels:
      label.set_fontsize(9)
    ticklabels = a.get_yticklabels()
    for label in ticklabels:
      label.set_fontsize(9)
    gray()
    imshow(-pix,vmin=-r1,vmax=-r2,aspect='equal',origin='lower',interpolation='nearest')
    try:
      for t in prf:
        if round(t[3],2) == round(emin,2):
          e=Ellipse((t[14],t[15]),2.*t[3],2.*t[3]*(1.-t[12]),t[13],fill=0)
          break
      e.set_clip_box(a.bbox)
      e.set_alpha(1.0)
      e.set_edgecolor('g')
      a.add_artist(e)
    except:
      pass

#  ion()
  draw()

def draw_fit():
  global ax,isfb,data,xmin,xmax,ymin,ymax,switch,sky,skysig,osky,pix,r1,r2,prf,emin,s1,s2,errsig
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2,origin
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic 
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge

  try:
    yd=(ymax-ymin)/20.
    xd=(xmax-xmin)/20.
    xstep=xmax/300.

    axis([xmin,xmax,ymax,ymin])

    if ifit == 2:
      try:
        t1=[] ; t2=[]
        b=1.9992*n_sersic-0.3271
        for i in range(301):
          t=i*xstep+xmin+xd
          t1.append((10.**t)**(1./4.))
          t2.append(se_sersic+(2.5*b)*((10.**t/re_sersic)**(1./n_sersic)-1.)/log(10.))
        ax.plot(t1,t2,'b--')
      except:
        pass
      text(xmin+xd,ymin+yd,'DeVaucouleur',color='b')
      ax.plot([xmin,xmax],[se_dev+8.325*((xmin**4./re_dev)**0.25-1.),se_dev+8.325*((xmax**4./re_dev)**0.25-1.)],'b-')
      text(xmin+xd,ymax-5.*yd,'$\\mu_e$ = '+('%5.2f' % se_dev))
      text(xmin+xd,ymax-4.*yd,'$r_e$ = '+('%5.2f' % re_dev))
      try:
        text(xmin+xd,ymax-1.*yd,'$\\chi^2$ = '+('%8.2e' % chisq_dev))
      except:
        pass
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymax,ymin)
      return

    if ifit in [1,3,4,6]:
      if ifit == 1:
        text(xmin+xd,ymin+yd,'Disk',color='b')
        try:
          text(xmin+xd,ymax-1.*yd,'$\\chi^2$ = '+('%8.2e' % chisq_disk))
        except:
          pass
      if ifit == 6:
        text(xmin+xd,ymin+yd,'Central Fit',color='b')
        try:
          text(xmin+xd,ymax-1.*yd,'$\\chi^2$ = '+('%8.2e' % chisq_disk))
        except:
          pass
      if ifit == 1:
        ax.plot([0.,xmax],[cstore,cstore+sstore*xmax],'b--')
      else:
        ax.plot([0.,xmax],[cstore,cstore+sstore*xmax],'r--')
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymax,ymin)
      text(xmin+xd,ymax-3.*yd,'$\\mu_o$ = '+('%5.2f' % cstore))
      alpha = 1.0857/sstore
      text(xmin+xd,ymax-2.*yd,'$\\alpha$ = '+('%5.2f' % alpha))

      if ifit in [3,4]:
        t1=[] ; t2=[]
        for i in range(301):
          t=i*xstep
          xnt=se_bulge+8.325*((t/re_bulge)**0.25-1.)
          xnt=-0.4*xnt
          xnt1=10.**xnt
          t1.append(t)
          t2.append(-2.5*log10(xnt1))
        ax.plot(t1,t2,'b--')
        ax.set_xlim(xmin,xmax)
        ax.set_ylim(ymax,ymin)

        t1=[] ; t2=[]
        for i in range(301):
          t=i*xstep
          xnt=se_bulge+8.325*((t/re_bulge)**0.25-1.)
          xnt=-0.4*xnt
          xnt1=10.**xnt
          xnt=cstore+sstore*t
          xnt=-0.4*xnt
          xnt2=10.**(xnt)
          xnt3=xnt1+xnt2
          t1.append(t)
          t2.append(-2.5*log10(xnt3))
        ax.plot(t1,t2,'b-')
        ax.set_xlim(xmin,xmax)
        ax.set_ylim(ymax,ymin)
        text(xmin+xd,ymax-5.*yd,'$\\mu_e$ = '+('%5.2f' % se_bulge))
        text(xmin+xd,ymax-4.*yd,'$r_e$ = '+('%5.2f' % re_bulge))
        try:
          text(xmin+xd,ymax-1.*yd,'$\\chi^2$ = '+('%8.2e' % chisq_bulge))
        except:
          pass
        if ifit == 3:
          text(xmin+xd,ymin+yd,'3P Bulge+Disk',color='b')
        else:
          text(xmin+xd,ymin+yd,'4P Bulge+Disk',color='b')

      xbm = se_bulge - 5.*log10(re_bulge) - 40.0
      alpha = 1.0857/sstore
      xdm = cstore - 5.*log10(alpha) - 38.6
      bdratio = 10.**(-0.4*(xbm - xdm))
      return

    if ifit == 5:
      text(xmin+xd,ymin+yd,'Sersic',color='b')
      t1=[] ; t2=[]
      b=1.9992*n_sersic-0.3271
      for i in range(301):
        t=i*xstep+xmin+xd
        t1.append(t)
        t2.append(se_sersic+(2.5*b)*((10.**t/re_sersic)**(1./n_sersic)-1.)/log(10.))
      ax.plot(t1,t2,'b-')
      text(xmin+xd,ymax-5.*yd,'$\\mu_e$ = '+('%5.2f' % se_sersic))
      text(xmin+xd,ymax-4.*yd,'$r_e$ = '+('%5.2f' % re_sersic))
      text(xmin+xd,ymax-3.*yd,'$n$ = '+('%5.2f' % n_sersic))
      try:
        text(xmin+xd,ymax-1.*yd,'$\\chi^2$ = '+('%8.2e' % chisq_sersic))
      except:
        pass
      try:
        t1=[] ; t2=[]
        for i in range(301):
          t=i*xstep+xmin+xd
          xnt=se_dev+8.325*((10.**t/re_dev)**0.25-1.)
          xnt=-0.4*xnt
          xnt1=10.**xnt
          t1.append(t)
          t2.append(-2.5*log10(xnt1))
        ax.plot(t1,t2,'b--')
      except:
        pass
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymax,ymin)
      return

  except:
    pass

def help():
  return '''
Usage: bdd options file_name

quick surface photometry calibration and fitting GUI

options: -h = this message
         -p = force sfb rebuild
         -a = auto sfb build
         -w = use internal sky marks
         -e = start in r^1/4 mode
         -s = start in Sersic mode

window #1 cursor commands:
c = contrast control   r = reset boundaries
z = zoom on points     x = delete point
s = set sky (2 hits)   i = show that ellipse
/ = write .sfb file    q = abort

window #2 cursor commands:

x = erase point        d = disk fit only
l = erase all min pts  b = do bulge+disk fit
u = erase all max pts  e = do r**1/4 fit only
r = reset deletions    s = sersic fit
c = central fit        p = toggle 3fit/4fit

, = set lower limit    . = set upper limit

q = abort              / = write .xml file and exit'''

def clicker(event):
  global ax,isfb,data,xmin,xmax,ymin,ymax,switch,sky,skysig,osky,pix,r1,r2,prf,emin,s1,s2,errsig
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2,origin
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic 
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge

  if not isfb: # look at raw data for sky

    if event.key == '/':
      ierr=0
      isfb=1
#      ifit=1
      tmp=[]
      for t in data:
        if t[1] - sky > 0 and t[2]: 
          err=abs(-2.5*log10((t[1]-sky)/(xscale**2))+cons- \
              (-2.5*log10((t[1]+t[3]-sky)/(xscale**2))+cons))
          if origin == '2MASS' and t[0]*xscale < 5.:
            tmp.append([t[0]*xscale,-2.5*log10((t[1]-sky)/(xscale**2))+cons,0,err])
#          elif origin == 'SDSS' and t[0]*xscale < 2.5:
#            tmp.append([t[0]*xscale,-2.5*log10((t[1]-sky)/(xscale**2))+cons,0,err])
          else:
            if (errsig > 0. and err > errsig) or ierr:
              ierr=1
              tmp.append([t[0]*xscale,-2.5*log10((t[1]-sky)/(xscale**2))+cons,0,err])
            else:
              tmp.append([t[0]*xscale,-2.5*log10((t[1]-sky)/(xscale**2))+cons,1,err])
      data=tmp

    if event.key == 'b':
       xmin=xmin-0.10*(xmax-xmin)
       xmax=xmax+0.10*(xmax-xmin)
       ymin=ymin-0.10*(ymax-ymin)
       ymax=ymax+0.10*(ymax-ymin)

    if event.key == 'q':
      disconnect(cid)
      close('all')
      time.sleep(0.5)
      sys.exit()

    if event.key == '?':
      print help()

    if event.key in [None,'shift','control','alt','right','left','up','down','escape']:
      pass

    if event.key == 'C':
      rold=r1
      k=event.xdata*1.5/(xmax-xmin)+0.5-1.5*xmin/(xmax-xmin)
      r1=r1*k
      if r1 < sky: r1=(rold-sky)/2.+sky
      r2=sky-0.05*r1-sky

    if event.key == 'z':
      rmin=1.e33
      for t in data:
        try:
          r=abs(t[0]-event.xdata)
        except:
          r=t[0]
        if r < rmin:
          rmin=r
          y=t[1]
      ymax=y+9.*abs(y-ymin)/10.
      ymin=data[-1][1]-3.*abs(data[-1][1]-ymin)/10.
#      ymax=sky+2.*skysig
#      ymin=sky-0.5*skysig
      for t in data:
        if t[1] < ymax:
          xmin=t[0]
          break

    if event.key == 'r':
      ymin=ymin_o
      ymax=ymax_o
      xmin=xmin_o

    if event.key == 'i':
      rmin=1.e33
      for t in data:
        r=abs(t[0]-event.xdata)
        if r < rmin:
          rmin=r
          emin=t[0]

    if event.key in ['x','1','2','3','4']:
      rmin=1.e33
      for i,t in enumerate(data):
        r=abs(t[0]-event.xdata)
        if r < rmin:
          rmin=r
          imin=i
        if event.key == '1' and t[0] > event.xdata and t[1] > event.ydata: data[i][2]=abs(data[i][2]-1)
        if event.key == '2' and t[0] < event.xdata and t[1] > event.ydata: data[i][2]=abs(data[i][2]-1)
        if event.key == '3' and t[0] < event.xdata and t[1] < event.ydata: data[i][2]=abs(data[i][2]-1)
        if event.key == '4' and t[0] > event.xdata and t[1] < event.ydata: data[i][2]=abs(data[i][2]-1)
      if event.key == 'x': data[imin][2]=abs(data[imin][2]-1)

    if event.key == 's':
      if not switch:
        switch=1
        s1=event.xdata
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' prf_sky_lower units=\'pixels\' '+str(s1), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
      else:
        switch=0
        s2=event.xdata
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' prf_sky_upper units=\'pixels\' '+str(s2), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        s=[]
        for t in data:
          if t[0] > s1 and t[0] < s2 and t[2]:
            s.append(t[1])
        t1,t2,e1,e2,t3,t4,t5=xits(s,3.)
        if str(e1) != 'nan':
          sky=e1
          skysig=e2
          p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                             ' prf_sky '+str(sky), \
                             shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
          tmp=os.waitpid(p.pid,0)

  else: # profile fitting

# ifit = 1, disk only fit
#      = 2, r^1/4 only fit
#      = 3, B+D fit, hold central disk sfb
#      = 4, B+D fit, all four parameters
#      = 5, Sersic fit

    if event.key == 'q':
      disconnect(cid)
      close('all')
      time.sleep(0.5)
      sys.exit()

    if event.key == '/':
      p=subprocess.Popen('xml_archangel -a '+sys.argv[-1].split('.')[0]+' sfb ', \
                          shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
      line='radius mu kill error\n'
      for z in data:
        line=line+'%.2f' % z[0]+' '+'%.3f' % z[1]+' '+'%1.1i' % z[2]+' '+'%.3f' % z[3]+'\n'
      p.communicate(line[:-1])
      try:
        tmp=os.waitpid(p.pid,0)
      except:
        pass

#      p=subprocess.Popen('xml_archangel -d '+sys.argv[-1].split('.')[0]+' re', \
#                        shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
#      tmp=os.waitpid(p.pid,0)

      disconnect(cid)
      close('all')
      time.sleep(0.5)
      sys.exit()

    if event.key == '?': 
      print help()

    if event.key == 'r':
#      for t in data: data[data.index(t)][2]=1
#      os.system('~/archangel/sfb/residuals.py '+sys.argv[-1].split('.')[0]+' &')
      p=subprocess.Popen('xml_archangel -a '+sys.argv[-1].split('.')[0]+' sfb ', \
                          shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
      line='radius mu kill error\n'
      for z in data:
        line=line+'%.2f' % z[0]+' '+'%.3f' % z[1]+' '+'%1.1i' % z[2]+' '+'%.3f' % z[3]+'\n'
      p.communicate(line[:-1])
      try:
        tmp=os.waitpid(p.pid,0)
      except:
        pass
      p=subprocess.Popen('~/archangel/sfb/residuals.py '+sys.argv[-1].split('.')[0], \
                   shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    if event.key in ['x','l','u']:
      rmin=1.e33
      if ifit == 5:
        ex=10.**(event.xdata)
      elif ifit == 2:
        ex=(event.xdata)**4.
      else:
        ex=event.xdata
      for t in data:
        if ifit == 5 or ifit == 2:
          for i,z in enumerate(data):
            try:
              for y in prf:
                if y[3] >= z[0]:
                  tmp=(z[0]*z[0]*(1.-y[12]))**0.5
                  break
            except:
              tmp=z[0]
        else:
          tmp=t[0]
        r=((tmp-ex)**2+(t[1]-event.ydata)**2)**0.5
        if r < rmin:
          rmin=r
          imin=data.index(t)

      if event.key == 'x':
        data[imin][2]=abs(data[imin][2]-1)
      else:
        for t in data:
          if ifit == 5 or ifit == 2:
            try:
              for y in prf:
                if y[3] >= t[0]:
                  tmp=(t[0]*t[0]*(1.-y[12]))**0.5
                  break
            except:
              tmp=t[0]
          else:
            tmp=t[0]
          if tmp >= ex and event.key == 'u': data[data.index(t)][2]=0
          if tmp <= ex and event.key == 'l': data[data.index(t)][2]=0

    if event.key == 'i':
      rmin=1.e33
      if ifit == 2:
        xtest=(event.xdata)**4
      elif ifit == 5:
        xtest=10.**(event.xdata)
      else:
        xtest=event.xdata
      for t in data:
        r=abs(t[0]-xtest)
        if r < rmin:
          rmin=r
          emin=t[0]

    if event.key == ',':
      x1=event.xdata
    if event.key == '.':
      x2=event.xdata

    if event.key == 'd':
      try:
        x1=lower_fit_disk
        x2=upper_fit_disk
      except:
        x1=event.xdata ; x2=data[-1][0]
      last_x1=x1 ; last_x2=x2
      ifit=1

    if event.key == 'c':
      x1=0.
      x2=5.
      ifit=6

    if event.key == 'e':
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

    if event.key == 'b':
      ifit=3

    if event.key == 's':
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
        if origin == 'SDSS': x1=log10(1.5)
      last_x1=x1 ; last_x2=x2
      ifit=5

    if event.key == 'p':
      if ifit == 3:
        ifit=4
      else:
        ifit=3

    if event.key in ['c','d','f','b','p','x','u','l'] or x1 != last_x1 or x2 != last_x2:
      last_x1=x1 ; last_x2=x2
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
          if ifit == 1:
            p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                               ' chisq_disk '+str(chisq_disk), \
                               shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            tmp=os.waitpid(p.pid,0)
            p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                               ' lower_fit_disk units=\'arcsecs\' '+str(x1), \
                               shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            tmp=os.waitpid(p.pid,0)
            p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                               ' upper_fit_disk units=\'arcsecs\' '+str(x2), \
                               shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            tmp=os.waitpid(p.pid,0)
            p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                               ' alpha units=\'arcsecs\' '+str(1.0857/sstore), \
                               shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            tmp=os.waitpid(p.pid,0)
            p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                               ' mu_o units=\'mags/arcsecs**2\' '+str(cstore), \
                               shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            tmp=os.waitpid(p.pid,0)
          else:
            p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                               ' chisq_central '+str(chisq_disk), \
                               shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            tmp=os.waitpid(p.pid,0)
            p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                               ' lower_fit_central units=\'arcsecs\' '+str(x1), \
                               shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            tmp=os.waitpid(p.pid,0)
            p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                               ' upper_fit_central units=\'arcsecs\' '+str(x2), \
                               shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            tmp=os.waitpid(p.pid,0)
            p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                               ' alpha_central units=\'arcsecs\' '+str(1.0857/sstore), \
                               shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            tmp=os.waitpid(p.pid,0)
            p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                               ' mu_c units=\'mags/arcsecs**2\' '+str(cstore), \
                               shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            tmp=os.waitpid(p.pid,0)
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
          
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' chisq_dev '+str(chisq_dev), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' re_dev units=\'arcsecs\' '+str(re_dev), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' se_dev units=\'mags/arcsecs**2\' '+str(se_dev), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        try:
          p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                             ' lower_fit_dev units=\'arcsecs\' '+str(x1**4), \
                             shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
          tmp=os.waitpid(p.pid,0)
          p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                             ' upper_fit_dev units=\'arcsecs\' '+str(x2**4), \
                             shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
          tmp=os.waitpid(p.pid,0)
        except:
          pass

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

        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' chisq_bulge '+str(chisq_bulge), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' re_bulge units=\'arcsecs\' '+str(re_bulge), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' se_bulge units=\'mags/arcsecs**2\' '+str(se_bulge), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' alpha units=\'arcsecs\' '+str(1.0857/sstore), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' mu_o units=\'mags/arcsecs**2\' '+str(cstore), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        alpha = 1.0857/sstore
        xbm = se_bulge - 5.*log10(re_bulge) - 40.0
        xdm = cstore - 5.*log10(alpha) - 38.6
        bdratio = 10.**(-0.4*(xbm - xdm))
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' bdratio '+str(bdratio), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        try:
          p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                             ' lower_fit_disk units=\'arcsecs\' '+str(x1), \
                             shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
          tmp=os.waitpid(p.pid,0)
          p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                             ' upper_fit_disk units=\'arcsecs\' '+str(x2), \
                             shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
          tmp=os.waitpid(p.pid,0)
        except:
          pass

      if ifit == 5:
        r=[] ; s=[]
        for t in data:
          try:
            for y in prf:
              if y[3] >= t[0]:
                tmp=(t[0]*t[0]*(1.-y[12]))**0.5
                if log10(tmp) > x1 and log10(tmp) < x2 and t[2]:
                  r.append(tmp) ; s.append(t[1])
                break
          except:
            if log10(t[0]) > x1 and log10(t[0]) < x2 and t[2]:
              r.append(t[0]) ; s.append(t[1])

        chisq_sersic,se_sersic,re_sersic,n_sersic=fit_sersic(len(r),r,s,se_sersic,re_sersic,n_sersic)

        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' chisq_sersic '+str(chisq_sersic), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' se_sersic units=\'mags/arcsecs**2\' '+str(se_sersic), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' re_sersic units=\'arcsecs\' '+str(re_sersic), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                           ' n_sersic '+str(n_sersic), \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        tmp=os.waitpid(p.pid,0)
        try:
          p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                             ' lower_fit_sersic units=\'arcsecs\' '+str(10.**x1), \
                             shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
          tmp=os.waitpid(p.pid,0)
          p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                             ' upper_fit_sersic units=\'arcsecs\' '+str(10.**x2), \
                             shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
          tmp=os.waitpid(p.pid,0)
        except:
          pass

  if event.key in ['shift'] and switch:
    pass
  else:
    clf() ; ax = fig.add_subplot(111)
    if isfb:
      plot_bdd()
    else:
      prf_plot()

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
      osky=float(elements['sky'][0][1])
    except:
      osky=0.

    try:
      sky=float(elements['prf_sky'][0][1])
    except:
      sky=osky

    try:
      skysig=float(elements['skysig'][0][1])
    except:
      skysig=1.

    try:
      s1=float(elements['prf_sky_lower'][0][1])
    except:
      s1=0

    try:
      s2=float(elements['prf_sky_upper'][0][1])
    except:
      pass

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
#      = 6, central fit only (mu_c)

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

    if '-c' in sys.argv:
      x1=0.
      x2=5.
      ifit=6

    if '-e' in sys.argv:
      ifit=2
      try:
        x1=lower_fit_dev**0.25
        x2=upper_fit_dev**0.25
      except:
        x1=0.
        x2=200.**0.25

    if '-s' in sys.argv:
      ifit=5
      try:
        x1=log10(lower_fit_sersic)
        x2=log10(upper_fit_sersic)
      except:
        x1=0.01
        x2=3.

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
          try:
            err1=prf[head.index('RMSRES')][z]/(prf[head.index('NUM')][z])**0.5
          except:
            err1=prf[head.index('RMSRES')][z]
          err2=skysig/(2.)**0.5 # note sqrt(2) kluge
          data.append([prf[head.index('RAD')][z],prf[head.index('INTENS')][z],1,(err1**2+err2**2)**0.5])
        tmp=array(prf)
        prf=swapaxes(tmp,1,0)
        if sys.argv[1] == '-p': break

    for t in elements['array']:
      if t[0]['name'] == 'sfb' and '-p' not in sys.argv:
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

  geo=eval(' '.join([tmp[:-1] for tmp in open(os.environ['ARCHANGEL_HOME']+'/.archangel','r').readlines()]))

  if 'prometheus' in os.uname()[1]:
    fig = figure(figsize=(12, 12), dpi=80)  # initialize plot parameters
    ax = fig.add_subplot(111)  # assign ax for text and axes
#    manager = plt.get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager.window.title('')
    manager.window.geometry('+1200+300') # move the window for deepcore big screen
  else:
    fig = figure(figsize=(9, 9), dpi=80)  # initialize plot parameters
    ax = fig.add_subplot(111)  # assign ax for text and axes
    manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager.window.title('')
    manager.window.geometry(geo['main_window'])
#    manager.window.geometry('+400+50')

  switch=0 ; grey=0 ; nx=100. ; ny=100. ; last_x1=x1 ; last_x2=x2

  for prefix in ['.fits','.fit','.raw']:
    if os.path.exists(sys.argv[-1].split('.')[0]+prefix):
      fitsobj=pyfits.open(sys.argv[-1].split('.')[0]+prefix,"readonly")
      nx=fitsobj[0].header['NAXIS1']
      ny=fitsobj[0].header['NAXIS2']
      pix=fitsobj[0].data
      fitsobj.close()
      r1=sky+50.*skysig
      r2=sky-0.05*(r1-sky)
      grey=1
      break

  if '-nogrey' in sys.argv: grey=0

  r=[] ; s=[]
  for t in data:
    if t[2]:
      r.append(t[0])
      s.append(t[1])
  xmin=min(r)-0.10*(max(r)-min(r))
  xmax=max(r)+0.10*(max(r)-min(r))

  if '-p' in sys.argv or not isfb:
    ymax=sky+30.*skysig
    ymin=sky-10.*skysig
  else:
    ymin=min(s)-0.10*(max(s)-min(s))
    ymax=max(s)+0.10*(max(s)-min(s))

  if '-w' in sys.argv:
    ymin=min(s)-0.10*(max(s)-min(s))
    ymax=max(s)+0.10*(max(s)-min(s))

  ymin_o=ymin ; ymax_o=ymax ; xmin_o=xmin

  if s1:
    s=[]
    for t in data:
      if t[0] > s1 and t[0] < s2 and t[2]:
        s.append(t[1])
    t1,t2,e1,e2,t3,t4,t5=xits(s,3.)
    if str(e1) != 'nan':
      sky=e1
      skysig=e2
      p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                         ' prf_sky '+str(sky), \
                         shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
      tmp=os.waitpid(p.pid,0)
      ymax=sky+30.*skysig
      ymin=sky-10.*skysig

  if '-errsig' in sys.argv:
    errsig=1.
  else:
    errsig=0.
    if origin == 'SDSS': errsig=1.25

  if '-p' in sys.argv: isfb=0

  if '-a' in sys.argv:
    if not s1:
      print '**** no prf_sky_lower, aborting ****'
      sys.exit()
    isfb=1
    auto_sfb()

  if isfb:
    plot_bdd()
  else:
    prf_plot()

  cid=connect('key_press_event',clicker)
  show()
