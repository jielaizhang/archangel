#!/usr/bin/env python

import sys, os.path, pyfits, time
from math import *
from xml_archangel import *
import subprocess
from pylab import *
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Ellipse
import warnings ; warnings.simplefilter('ignore')

def plot_bdd():
  global ax,isfb,data,xmin,xmax,ymin,ymax,switch,sky,skysig,pix,r1,r2,prf,emin,s1,s2
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic 
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge

#  ioff() # hold drawing until everything is done

  ifit=5

  x1=log10(lower_fit_dev)
  x2=log10(upper_fit_dev)

  r=[] ; s=[] ; v=[] ; w=[] ; e=[]
  for t in data:
    for y in prf:
      if y[3] >= t[0]:
        tmp=(t[0]*t[0]*(1.-y[12]))**0.5
        break
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
  if len(v) > 0: ax.scatter(v,w,s=75,marker=(4,2,pi/4.),color='r')
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
        if numpy.isnan(lasty+(x1-lastx)*(t[1]-lasty)/(t1-lastx)+0.03*(ymax-ymin)): raise
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
      try:
        if numpy.isnan(lasty+(x1-lastx)*(t[1]-lasty)/(t1-lastx)+0.03*(ymax-ymin)): raise
        if lasty+(x2-lastx)*(t[1]-lasty)/(t1-lastx)+0.03*(ymax-ymin) < ymax:
          text(x2,lasty+(x2-lastx)*(t[1]-lasty)/(t1-lastx)+0.03*(ymax-ymin),'$\uparrow$',color='g', \
               horizontalalignment='center',verticalalignment='center')
        else:
          text(x2,t[1]+0.03*(ymax-ymin),'$\uparrow$',color='g', \
               horizontalalignment='center',verticalalignment='center')
      except:
        text(x2,t[1]+0.05*(ymax-ymin),'$\uparrow$',color='g', \
             horizontalalignment='center',verticalalignment='center')
  except:
    pass

  n=0
  for x,y,err in zip(r,s,e):
    n+=1
    if err > abs(ymax-ymin)/200. and err > .1: errorbar(x,y,yerr=err,ecolor='k')

  draw_fit()

#  ion()
  draw()

def draw_fit():
  global ax,isfb,data,xmin,xmax,ymin,ymax,switch,sky,skysig,pix,r1,r2,prf,emin,s1,s2
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2
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
Usage: compare_dev

plot dev vs sersic from auto_fit'''

def clicker(event):
  global ax,isfb,data,xmin,xmax,ymin,ymax,switch,sky,skysig,pix,r1,r2,prf,emin,s1,s2
  global x1,x2,cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit,last_x1,last_x2
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic 
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge

# ifit = 1, disk only fit
#      = 2, r^1/4 only fit
#      = 3, B+D fit, hold central disk sfb
#      = 4, B+D fit, all four parameters
#      = 5, Sersic fit

  if event.key == '/':
    disconnect(cid)
    close('all')
    time.sleep(0.5)
    sys.exit()

  if event.key in ['shift'] and switch:
    pass


if __name__ == '__main__':

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
      re_dev=float(elements['re_dev'][0][1])
      se_dev=float(elements['se_dev'][0][1])
      lower_fit_dev=float(elements['lower_fit_dev'][0][1])
      upper_fit_dev=float(elements['upper_fit_dev'][0][1])
      chisq_dev=float(elements['chisq_dev'][0][1])
    except:
      pass

    try:
      re_sersic=float(sys.argv[-3])
      se_sersic=float(sys.argv[-4])
      n_sersic=float(sys.argv[-2])
      lower_fit_sersic=float(elements['lower_fit_sersic'][0][1])
      upper_fit_sersic=float(elements['upper_fit_sersic'][0][1])
      chisq_sersic=float(elements['chisq_sersic'][0][1])
    except:
      pass

    try:
      origin=elements['origin'][0][1]
    except:
      origin=None

    isfb=1

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

  geo=eval(' '.join([tmp[:-1] for tmp in open(os.environ['ARCHANGEL_HOME']+'/.archangel','r').readlines()]))

  if 'deepcore' in os.uname()[1]:
    fig = figure(figsize=(12, 12), dpi=80)  # initialize plot parameters
    ax = fig.add_subplot(111)  # assign ax for text and axes
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

  plot_bdd()

  ifit=5
  cid=connect('key_press_event',clicker)
  show()
