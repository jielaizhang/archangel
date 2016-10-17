#!/usr/bin/env python

import sys, time
import astropy.io.fits as pyfits
from math import *
from xml_archangel import *
import xits
from pylab import *
from matplotlib.ticker import MultipleLocator

def clicker(event):

  if event.key == '/':
    disconnect(cid)
    close('all')
    time.sleep(0.5)
    sys.exit()

  if event.key in ['shift']:
    pass
  else:
    draw_plot()

def draw_plot():
  ax1 = fig.add_axes([0.2,0.1,0.6,0.3]) #left, bottom, width, height

  r=[] ; s=[] ; v=[] ; w=[] ; e=[]
  for t in data:
    if t[2]:
      r.append(log10(t[0]))
      s.append(t[1])
      e.append(t[3])
    else:
      v.append(log10(t[0]))
      w.append(t[1])

# set limits, check for data inside image frame
  xmin=min(r+v)-0.10*(max(r+v)-min(r+v))
  xmax=max(r+v)+0.10*(max(r+v)-min(r+v))
  ymin=min(s+w)-0.10*(max(s+w)-min(s+w))
  ymax=max(s+w)+0.10*(max(s+w)-min(s+w))

  isw=1
  while (isw):
    isw=0
    for t in data:
      t1=log10(t[0])
      if t1 > xmin+(xmax-xmin)/1.8 and t[1] < ymax-(ymax-ymin)/1.8:
        isw=1
        xmax=xmax+0.10*(xmax-xmin)
        ymin=ymin-0.10*(ymax-ymin)

  ax1.axis([xmin,xmax,ymax,ymin])
  ax1.scatter(r,s,s=75,marker=(4,0,0),facecolor=(1,1,1,0),color='k')
  if len(v) > 0: ax1.scatter(v,w,s=75,marker=(4,2,pi/4.),color='r')

  try:
    if str(x1) != 'nan' or str(x2) != 'nan':
      for t in data:
        t1=log10(t[0])
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
        t1=log10(t[0])
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

  xstep=xmax/300.
  xd=(xmax-xmin)/20.
  yd=(ymax-ymin)/20.
  t1=[] ; t2=[]
  b=1.9992*n_sersic-0.3271
  for i in range(301):
    t=i*xstep+xmin+xd
    t1.append(t)
    t2.append(se_sersic+(2.5*b)*((10.**t/re_sersic)**(1./n_sersic)-1.)/log(10.))
  ax1.plot(t1,t2,'b-')
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
    ax1.plot(t1,t2,'b--')
  except:
    pass

  xlabel('log r (arcsec)')
  ylabel('mag/arcsec$^{-2}$')
  ax1.set_xlim(xmin,xmax)
  ax1.set_ylim(ymax,ymin)

  if grey:
    a = axes([.60,.23,.18,.18]) #left, bottom, width, height
    ticklabels = a.get_xticklabels()
    for label in ticklabels:
      label.set_fontsize(9)
    ticklabels = a.get_yticklabels()
    for label in ticklabels:
      label.set_fontsize(9)
    gray()
    imshow(-pix,vmin=-r1,vmax=-r2,aspect='equal',origin='lower',interpolation='nearest')

  ax2 = fig.add_axes([0.2,0.40,0.6,0.12])
  s=[[],[]] ; v=[[],[]] ; w=[[],[]]
  for t in prf:
    if t[6] != 1:
      if t[6] == -1:
        w[0].append(log10(t[3]))
        w[1].append(1.-t[12])
      elif t[6] < -1:
        v[0].append(log10(t[3]))
        v[1].append(1.-t[12])
      else:
        s[0].append(log10(t[3]))
        s[1].append(1.-t[12])
  ax2.axis([xmin,xmax,0.55,1.05])
  ax2.scatter(s[0],s[1],s=75,marker=(4,2,pi/4.),facecolor=(1,1,1,0),color='k')
  if len(v[0]) > 0: ax2.scatter(v[0],v[1],s=75,marker=(4,2,pi/4.),color='r')
  if len(w[0]) > 0: ax2.scatter(w[0],w[1],s=75,marker=(4,2,pi/4.),color='g')
  ylabel('b/a')
  ax2.set_xlim(xmin,xmax)
  ax2.set_ylim(0.55,1.05)

  ax3 = fig.add_axes([0.2,0.52,0.6,0.12])
  s=[[],[]] ; v=[[],[]] ; w=[[],[]] ; ymin=1.e33 ; ymax=-1.e33
  for t in prf:
    if t[6] != 1:
      if t[6] == -1:
        w[0].append(log10(t[3]))
        w[1].append(t[13])
      elif t[6] < -1:
        v[0].append(log10(t[3]))
        v[1].append(t[13])
      else:
        s[0].append(log10(t[3]))
        s[1].append(t[13])
      if t[13] > ymax: ymax=t[13]
      if t[13] < ymin: ymin=t[13]
  ymin=ymin-0.10*(ymax-ymin)
  ymax=ymax+0.10*(ymax-ymin)
  ax3.axis([xmin,xmax,ymin,ymax])
  ax3.scatter(s[0],s[1],s=75,marker=(4,2,pi/4.),facecolor=(1,1,1,0),color='k')
  if len(v[0]) > 0: ax3.scatter(v[0],v[1],s=75,marker=(4,2,pi/4.),color='r')
  if len(w[0]) > 0: ax3.scatter(w[0],w[1],s=75,marker=(4,2,pi/4.),color='g')
  ylabel('PA (degs)')
  ax3.set_xlim(xmin,xmax)
  ax3.set_ylim(ymin,ymax)

  ax4 = fig.add_axes([0.2,0.64,0.6,0.12])
  s1=[[],[]] ; v1=[[],[]] ; w1=[[],[]] ; ymin=1.e33 ; ymax=-1.e33
  for t in prf:
    if t[6] != 1:
      if t[6] == -1:
        w1[0].append(log10(t[3]))
        w1[1].append(t[14]-prf[0][14])
      elif t[6] < -1:
        v1[0].append(log10(t[3]))
        v1[1].append(t[14]-prf[0][14])
      else:
        s1[0].append(log10(t[3]))
        s1[1].append(t[14]-prf[0][14])
      if t[14]-prf[0][14] > ymax: ymax=t[14]-prf[0][14]
      if t[14]-prf[0][14] < ymin: ymin=t[14]-prf[0][14]
  s2=[[],[]] ; v2=[[],[]] ; w2=[[],[]]
  for t in prf:
    if t[6] != 1:
      if t[6] == -1:
        w2[0].append(log10(t[3]))
        w2[1].append(t[15]-prf[0][15])
      elif t[6] < -1:
        v2[0].append(log10(t[3]))
        v2[1].append(t[15]-prf[0][15])
      else:
        s2[0].append(log10(t[3]))
        s2[1].append(t[15]-prf[0][15])
      if t[15]-prf[0][15] > ymax: ymax=t[15]-prf[0][15]
      if t[15]-prf[0][15] < ymin: ymin=t[15]-prf[0][15]
  ymin=ymin-0.10*(ymax-ymin)
  ymax=ymax+0.10*(ymax-ymin)
  ax4.axis([xmin,xmax,ymin,ymax])
  ax4.scatter(s1[0],s1[1],s=75,marker=(4,2,pi/4.),facecolor=(1,1,1,0),color='k')
  if len(v[0]) > 0: ax4.scatter(v1[0],v1[1],s=75,marker=(4,2,pi/4.),color='r')
  if len(w[0]) > 0: ax4.scatter(w1[0],w1[1],s=75,marker=(4,2,pi/4.),color='g')
  ax4.scatter(s2[0],s2[1],s=75,marker=(4,2,pi/2.),facecolor=(1,1,1,0),color='k')
  if len(v[0]) > 0: ax4.scatter(v2[0],v2[1],s=75,marker=(4,2,pi/2.),color='r')
  if len(w[0]) > 0: ax4.scatter(w2[0],w2[1],s=75,marker=(4,2,pi/2.),color='g')
  ylabel('$x_c:y_c$')
  ax4.set_xlim(xmin,xmax)
  ax4.set_ylim(ymin,ymax)

  ax5 = fig.add_axes([0.2,0.76,0.6,0.12])
  r=[] ; s=[] ; ymin=1.e33 ; ymax=-1.e33
  for t in colors:
    r.append(log10(t[0]))
    s.append(t[1])
    if t[1] > ymax: ymax=t[1]
    if t[1] < ymin: ymin=t[1]
  ymin=xits.xits(s,3.)[2]-xits.xits(s,3.)[1]/2.
  ymax=xits.xits(s,3.)[2]+xits.xits(s,3.)[1]/2.
#  ymin=ymin-0.10*(ymax-ymin)
#  ymax=ymax+0.10*(ymax-ymin)
  ax5.axis([xmin,xmax,ymin,ymax])
  ax5.scatter(r,s,s=75,marker=(4,2,pi/4),facecolor=(1,1,1,0),color='k')
  ylabel('J-K')
  ax5.set_xlim(xmin,xmax)
  ax5.set_ylim(ymin,ymax)
  title(sys.argv[-1])

  for ax in ax2,ax3,ax4,ax5:
    for label in ax.get_xticklabels():
      label.set_visible(False)

if __name__ == '__main__':

  if sys.argv[1] == '-h':
    print 'no help'
    sys.exit()

  if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
    doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

# ifit = 1, disk only fit
#      = 2, r^1/4 only fit
#      = 3, B+D fit, hold central disk sfb
#      = 4, B+D fit, all four parameters
#      = 5, Sersic fit

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
      re_sersic=float(elements['re_sersic'][0][1])
      se_sersic=float(elements['se_sersic'][0][1])
      n_sersic=float(elements['n_sersic'][0][1])
      lower_fit_sersic=float(elements['lower_fit_sersic'][0][1])
      upper_fit_sersic=float(elements['upper_fit_sersic'][0][1])
      chisq_sersic=float(elements['chisq_sersic'][0][1])
    except:
      pass

    for t in elements['array']:
      if t[0]['name'] == 'colors':
        colors=[]
        head=[]
        pts=[]
        for z in t[2]['axis']:
          head.append(z[0]['name'])
          pts.append(map(float,z[1].split('\n')))
        for z in range(len(pts[0])):
          tmp=[]
          for w in head:
            tmp.append(pts[head.index(w)][z])
          colors.append(tmp)

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
# don't do this, causes small nummercal errors in iso_prf
#          if tmp[13] >= 270: tmp[13]=tmp[13]-360.
#          if tmp[13] > 90: tmp[13]=tmp[13]-180.
#          if tmp[13] <= -270: tmp[13]=tmp[13]+360.
#          if tmp[13] < -90: tmp[13]=tmp[13]+180.
          prf.append(tmp)

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

    sky=float(elements['sky'][0][1])
    skysig=float(elements['skysig'][0][1])
  else:
    print sys.argv[-1],'XML file not found - aborting'
    sys.exit()

  if os.path.exists(sys.argv[-1].split('.')[0]+'.fits'):
    fitsobj=pyfits.open(sys.argv[-1].split('.')[0]+'.fits',"readonly")
    nx=fitsobj[0].header['NAXIS1']
    ny=fitsobj[0].header['NAXIS2']
    pix=fitsobj[0].data
    fitsobj.close()
    r1=sky+50.*skysig
    r2=sky-0.05*(r1-sky)
    grey=1
  else:
    grey=0

  if 'prometheus' in os.uname()[1]:
    fig = figure(figsize=(12, 16), dpi=80)  # initialize plot parameters
    manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager.window.title('')
    manager.window.geometry('+1200+100') # move the window for deepcore big screen
  else:
    fig = figure(figsize=(9, 9), dpi=80)  # initialize plot parameters
    manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager.window.title('')
    manager.window.geometry('+400+50')

  draw_plot()
  cid=connect('key_press_event',clicker)
  show()
