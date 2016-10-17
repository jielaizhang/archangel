#!/usr/bin/env python

import sys, os.path, pyfits, time
from math import *
from xml_archangel import *
import subprocess
from pylab import *
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Ellipse

def fchisq(s,sigmay,npts,nfree,yfit):
  chisq=0.
  for j in range(npts):
    chisq=chisq+((s[j]-yfit[j])**2)/sigmay[j]**2
  return chisq/nfree

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

def plot_bdd():
  global ax,isfb,data,xmin,xmax,ymin,ymax,switch,sky,skysig,pix,r1,r2,prf,emin,s1,s2,errsig
  global x1,x2,cstore1,sstore1,cstore2,sstore2,ifit,last_x1,last_x2
  global lower_fit_disk,upper_fit_disk,midpt,last_mid,chisq_disk

#  ioff() # hold drawing until everything is done
  r=[] ; s=[] ; v=[] ; w=[] ; e=[]
  for t in data:
    try:
      for y in prf:
        if y[3] >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          break
    except:
      tmp=t[0]
    if t[2]:
      r.append(t[0])
      s.append(t[1])
      e.append(t[3])
    else:
      v.append(t[0])
      w.append(t[1])

# set limits, check for data inside image frame
  xmin=min(r)-0.10*(max(r)-min(r))
  xmax=max(r)+0.10*(max(r)-min(r))
  ymin=min(s)-0.10*(max(s)-min(s))
  ymax=max(s)+0.10*(max(s)-min(s))

  isw=1
  while (isw):
    isw=0
    for t in data:
      t1=t[0]
      if t1 > xmin+(xmax-xmin)/2.2 and t[1] < ymax-(ymax-ymin)/2.2:
        isw=1
        xmax=xmax+0.10*(xmax-xmin)
        ymin=ymin-0.10*(ymax-ymin)

  axis([xmin,xmax,ymax,ymin])
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

      for t in data:
        t1=t[0]
        if t1 > midpt: break
        lastx=t1
        lasty=t[1]
      if lasty+(midpt-lastx)*(t[1]-lasty)/(t1-lastx)+0.03*(ymax-ymin) < ymax:
        text(midpt,lasty+(midpt-lastx)*(t[1]-lasty)/(t1-lastx)+0.03*(ymax-ymin),'$\uparrow$',color='r', \
             horizontalalignment='center',verticalalignment='center')
      else:
        text(midpt,ymax-0.03*(ymax-ymin),'$\uparrow$',color='r', \
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
  global ax,isfb,data,xmin,xmax,ymin,ymax,switch,sky,skysig,pix,r1,r2,prf,emin,s1,s2,errsig
  global x1,x2,cstore1,sstore1,cstore2,sstore2,ifit,last_x1,last_x2
  global lower_fit_disk,upper_fit_disk,midpt,last_mid,chisq_disk

  try:
    yd=(ymax-ymin)/20.
    xd=(xmax-xmin)/20.
    xstep=xmax/300.

    axis([xmin,xmax,ymax,ymin])

    text(xmin+xd,ymin+yd,'Disk',color='b')
    try:
      text(xmin+xd,ymax-1.*yd,'$\\chi^2$ = '+('%8.2e' % chisq_disk))
    except:
      pass
    ax.plot([0.,xmax],[cstore1,cstore1+sstore1*xmax],'m--')
    ax.plot([0.,xmax],[cstore2,cstore2+sstore2*xmax],'b--')

    ax.set_xlim(xmin,xmax)
    ax.set_ylim(ymax,ymin)
    text(xmin+xd,ymax-3.*yd,'$\\mu_o$ = '+('%5.2f' % cstore1))
    alpha = 1.0857/sstore1
    text(xmin+xd,ymax-2.*yd,'$\\alpha$ = '+('%5.2f' % alpha))

  except:
    pass

def help():
  return '''
Usage: double_exp file_name

quick double exp fit to LSB's

options: -h = this message

x = erase point        r = reset deletions  
l = erase all min pts  u = erase all max pts
, = set lower limit    . = set upper limit
q = abort              / = write .xml file and exit'''

def clicker(event):
  global ax,isfb,data,xmin,xmax,ymin,ymax,switch,sky,skysig,pix,r1,r2,prf,emin,s1,s2,errsig
  global x1,x2,cstore1,sstore1,cstore2,sstore2,ifit,last_x1,last_x2
  global lower_fit_disk,upper_fit_disk,midpt,last_mid,chisq_disk

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
    p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                       ' midpt '+str(midpt), \
                       shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=os.waitpid(p.pid,0)
    p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                       ' inner_alpha units=\'arcsecs\' '+str(1.0857/sstore1), \
                       shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=os.waitpid(p.pid,0)
    p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                       ' inner_mu_o units=\'mags/arcsecs**2\' '+str(cstore1), \
                       shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=os.waitpid(p.pid,0)
    p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                       ' outer_alpha units=\'arcsecs\' '+str(1.0857/sstore2), \
                       shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=os.waitpid(p.pid,0)
    p=subprocess.Popen('xml_archangel -e '+sys.argv[-1].split('.')[0]+ \
                       ' outer_mu_o units=\'mags/arcsecs**2\' '+str(cstore2), \
                       shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=os.waitpid(p.pid,0)

    disconnect(cid)
    close('all')
    time.sleep(0.5)
    sys.exit()

  if event.key == '?': 
    print help()

  if event.key in ['x','l','u']:
    rmin=1.e33
    if ifit == 5:
      ex=10.**(event.xdata)
    else:
      ex=event.xdata
    for t in data:
      r=((t[0]-ex)**2+(t[1]-event.ydata)**2)**0.5
      if r < rmin:
        rmin=r
        imin=data.index(t)
    if event.key == 'x':
      data[imin][2]=abs(data[imin][2]-1)
    else:
      for t in data:
        if t[0] >= ex and event.key == 'u': data[data.index(t)][2]=0
        if t[0] <= ex and event.key == 'l': data[data.index(t)][2]=0

  if event.key == 'i':
    rmin=1.e33
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

  if event.key == 'b':
    midpt=event.xdata

  if x1 != last_x1 or x2 != last_x2 or last_mid != midpt:
    last_x1=x1 ; last_x2=x2 ; last_mid=midpt
    fit=[]

    if ifit == 1:
      for t in data:
        if t[0] > x1 and t[0] < midpt and t[2]:
          fit.append([t[0],t[1],1.])
      if len(fit) > 2:
        a1,b1,r,sigb,sigm,sig=linfit(fit)

      try:
        xmean=0. ; sig=[]
        for t in fit:
          if t[0] > x1 and t[0] < midpt and t[2]:
            xmean=xmean+perp(b1,a1,t[0],t[1])
            sig.append(perp(b1,a1,t[0],t[1]))
        xmean=xmean/len(sig)
        sigma=0.
        for tmp in sig:
          sigma=sigma+(xmean-tmp)**2
        sigma=(sigma/(len(sig)-1.))**0.5
      except:
        raise
      fit=[]
      for t in data:
        if t[0] > x1 and t[0] < midpt and t[2]:
          ss=abs(perp(b1,a1,t[0],t[1])/sigma)
          if ss < .5: ss=.5
          fit.append([t[0],t[1],ss])
      if len(fit) > 2:
        a1,b1,rx,sigbx,sigmx,sigx=linfit(fit)

      fit=[]
      for t in data:
        if t[0] > midpt and t[0] < x2 and t[2]:
          fit.append([t[0],t[1],1.])
      if len(fit) > 2:
        a2,b2,r,sigb,sigm,sig=linfit(fit)
      try:
        xmean=0. ; sig=[]
        for t in fit:
          if t[0] > midpt and t[0] < x2 and t[2]:
            xmean=xmean+perp(b2,a2,t[0],t[1])
            sig.append(perp(b2,a2,t[0],t[1]))
        xmean=xmean/len(sig)
        sigma=0.
        for tmp in sig:
          sigma=sigma+(xmean-tmp)**2
        sigma=(sigma/(len(sig)-1.))**0.5
      except:
        pass
      fit=[]
      for t in data:
        if t[0] > midpt and t[0] < x2 and t[2]:
          ss=abs(perp(b2,a2,t[0],t[1])/sigma)
          if ss < .5: ss=.5
          fit.append([t[0],t[1],ss])
      if len(fit) > 2:
        a2,b2,rx,sigbx,sigmx,sigx=linfit(fit)

      sstore1=b1 ; cstore1=a1
      sstore2=b2 ; cstore2=a2

  if event.key in ['shift'] and switch:
    pass
  else:
    clf() ; ax = fig.add_subplot(111)
    plot_bdd()

if __name__ == '__main__':

# runtime warnings
  import warnings
  warnings.filterwarnings('ignore')

  if sys.argv[1] == '-h':
    print help()
    sys.exit()

  x1=x2=cstore=sstore=re_bulge=se_bulge=re_dev=se_dev=re_sersic=se_sersic=n_sersic='nan'
  ifit=1

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

# ifit = 1, disk only fit
#      = 2, r^1/4 only fit
#      = 3, B+D fit, hold central disk sfb
#      = 4, B+D fit, all four parameters
#      = 5, Sersic fit
#      = 6, central fit only (mu_c)

    try:
      cstore1=float(elements['mu_o'][0][1])
      cstore2=cstore1
      sstore1=1.0857/float(elements['alpha'][0][1])
      sstore2=sstore1
      x1=lower_fit_disk=float(elements['lower_fit_disk'][0][1])
      x2=upper_fit_disk=float(elements['upper_fit_disk'][0][1])
      chisq_disk=float(elements['chisq_disk'][0][1])
      ifit=1
    except:
      pass

    for t in elements['array']:
      if t[0]['name'] == 'sfb':
        isfb=1
        data=[]
        tmp=[]
        head=[]
        for z in t[2]['axis']:
          head.append(z[0]['name'])
          tmp.append(map(float,z[1].split('\n')))
        for z in range(len(tmp[0])):
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

  switch=0 ; grey=0 ; nx=100. ; ny=100. ; last_x1=x1 ; last_x2=x2 ; midpt=(x2-x1)/2. ; last_mid=midpt

  for prefix in ['.fits','.fit']:
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
  ymin=min(s)-0.10*(max(s)-min(s))
  ymax=max(s)+0.10*(max(s)-min(s))
  ymin_o=ymin ; ymax_o=ymax ; xmin_o=xmin

  if '-errsig' in sys.argv:
    errsig=1.
  else:
    errsig=0.

  plot_bdd()
  cid=connect('key_press_event',clicker)
  show()
