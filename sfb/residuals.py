#!/usr/bin/env python

# warning, note 2MASS switch, no plot inside 2"

import sys, time
from math import *
from xml_archangel import *
from pylab import *
from matplotlib.ticker import MultipleLocator
import astropy.io.fits as pyfits

def clicker(event):
  global xmin,xmax,ymin,ymax,data,fig,ax
  global cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge

  if event.key == '/':
    disconnect(cid)
    close('all')
    time.sleep(0.5)
    sys.exit()

#  if event.key in ['h']:
#    draw_plot(True)
#    fig.savefig('pick.pdf')
#    disconnect(cid)
#    close('all')
#    time.sleep(0.5)
#    sys.exit()

  if event.key in ['shift']:
    pass
  else:
    draw_plot(False)

def draw_plot(usetex):
  global xmin,xmax,ymin,ymax,data,fig,ax
  global cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge

#  ioff()

  rc('text',usetex=True)

  ymin=+0.5 ; ymax=-0.5
  suptitle(r'\rm '+sys.argv[-1].split('_')[0])
  yd=(ymax-ymin)/8.
  xd=(xmax-xmin)/40.
  r=[] ; s=[] ; v=[] ; w=[] ; e=[]
  try:
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
        r.append(log10(t[0])) ; s.append(t[1]-xnt3) ; e.append(t[3])
      else:
        v.append(log10(t[0])) ; w.append(t[1]-xnt3)

    ax1 = fig.add_axes([0.2,0.1,0.6,0.15]) #left, bottom, width, height
    ax1.axis([xmin,xmax,ymin,ymax])
#    ax1.scatter(r,s,s=75,marker=(4,0,0),facecolor=(1,1,1,0),color='k')
    ax1.scatter(r,s,s=75,marker=(4,0,0),color='k')
    if len(v) > 0: ax1.scatter(v,w,s=75,marker=(4,2,pi/4.),color='r')
    ax1.plot([xmin,xmax],[0.,0.],'b-')
    for x,y,err in zip(r,s,e):
      if err > .1 and err < .4: errorbar(x,y,yerr=err,ecolor='k')
    alpha = 1.0857/sstore
    text(xmin+xd,ymax-1.5*yd,'Bulge+Disk: $\\mu_o$ = '+('%5.2f' % cstore)+ \
                                     ', $\\alpha$ = '+('%5.2f' % alpha)+ \
                                     ', $\\mu_e$ = '+('%5.2f' % se_bulge)+ \
                                     ', $r_e$ = '+('%5.2f' % re_bulge),fontsize=12)
#    text(log10(lower_fit_disk),0.1,'$\uparrow$',color='g', \
#         horizontalalignment='center',verticalalignment='center')
#    text(log10(upper_fit_disk),0.1,'$\uparrow$',color='g', \
#         horizontalalignment='center',verticalalignment='center')
    text(xmin+5.*xd,ymin+yd/4.,'$\\chi^2$ = '+('%8.2e' % chisq_bulge),fontsize=12)
    ylabel('$\Delta\mu$')
    ax1.set_xlim(xmin,xmax)
    ax1.set_ylim(ymin,ymax)
    xlabel('log r')
  except:
    pass

  try:
    r=[] ; s=[] ; v=[] ; w=[] ; e=[]
    a=[se_dev,re_dev]
    for t in data:
      for y in prf:
        if y[3] >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          break
      else:
        tmp=(t[0]*t[0]*(1.-prf[-1][12]))**0.5
      xnt1 = a[0] + 8.325*((tmp/a[1])**0.25 - 1.0)
      if t[2]:
        r.append(log10(tmp)) ; s.append(t[1]-xnt1) ; e.append(t[3])
      else:
        v.append(log10(tmp)) ; w.append(t[1]-xnt1)

    ax2 = fig.add_axes([0.2,0.25,0.6,0.15]) #left, bottom, width, height
    ax2.axis([xmin,xmax,ymin,ymax])
#    ax2.scatter(r,s,s=75,marker=(4,0,0),facecolor=(1,1,1,0),color='k')
    ax2.scatter(r,s,s=75,marker=(4,0,0),color='k')
    if len(v) > 0: ax2.scatter(v,w,s=75,marker=(4,2,pi/4.),color='r')
    ax2.plot([xmin,xmax],[0.,0.],'b-')
    for x,y,err in zip(r,s,e):
      if err > .1 and err < .4: errorbar(x,y,yerr=err,ecolor='k')
    text(xmin+xd,ymax-1.5*yd,'DeV: $\\mu_e$ = '+('%5.2f' % se_dev)+ \
                           ', $r_e$ = '+('%5.2f' % re_dev),fontsize=12)
    text(log10(lower_fit_dev),0.1,'$\uparrow$',color='g', \
         horizontalalignment='center',verticalalignment='center')
    text(log10(upper_fit_dev),0.1,'$\uparrow$',color='g', \
         horizontalalignment='center',verticalalignment='center')
    text(xmin+5.*xd,ymin+yd/4.,'$\\chi^2$ = '+('%8.2e' % chisq_dev),fontsize=12)
    ylabel('$\Delta\mu$')
    ax2.set_xlim(xmin,xmax)
    ax2.set_ylim(ymin,ymax)
  except:
    pass

  try:
    r=[] ; s=[] ; v=[] ; w=[] ; e=[]
    a=[se_sersic,re_sersic,n_sersic]
    for t in data:
      for y in prf:
        if y[3] >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          break
      else:
        tmp=(t[0]*t[0]*(1.-prf[-1][12]))**0.5
      b=2.*a[2]-(1./3.)
      xnt1=-2.5*log10((10.**(a[0]/-2.5))*exp(-b*((tmp/a[1])**(1./a[2])-1.)))
      if t[2]:
#        print log10(tmp),t[1],xnt1,t[1]-xnt1
        r.append(log10(tmp)) ; s.append(t[1]-xnt1) ; e.append(t[3])
      else:
        v.append(log10(tmp)) ; w.append(t[1]-xnt1)

    ax3 = fig.add_axes([0.2,0.40,0.6,0.15]) #left, bottom, width, height
    ax3.axis([xmin,xmax,ymin,ymax])
#    ax3.scatter(r,s,s=75,marker=(4,0,0),facecolor=(1,1,1,0),color='k')
    ax3.scatter(r,s,s=75,marker=(4,0,0),color='k')
    if len(v) > 0: ax3.scatter(v,w,s=75,marker=(4,2,pi/4.),color='r')
    ax3.plot([xmin,xmax],[0.,0.],'b-')
    for x,y,err in zip(r,s,e):
      if err > .1 and err < .4: errorbar(x,y,yerr=err,ecolor='k')
    text(xmin+xd,ymax-1.5*yd,'Sersic: $\\mu_e$ = '+('%5.2f' % se_sersic)+ \
                             ', $r_e$ = '+('%5.2f' % re_sersic)+ \
                             ', n = '+('%5.2f' % n_sersic),fontsize=12)
    text(log10(lower_fit_sersic),0.1,'$\uparrow$',color='g', \
         horizontalalignment='center',verticalalignment='center')
    text(log10(upper_fit_sersic),0.1,'$\uparrow$',color='g', \
         horizontalalignment='center',verticalalignment='center')
    text(xmin+5.*xd,ymin+yd/4.,'$\\chi^2$ = '+('%8.2e' % chisq_sersic),fontsize=12)
    ylabel('$\Delta\mu$')
    ax3.set_xlim(xmin,xmax)
    ax3.set_ylim(ymin,ymax)
  except:
    pass

  ax4 = fig.add_axes([0.2,0.55,0.6,0.15]) #left, bottom, width, height
  s=[[],[],[]] ; v=[[],[],[]] ; w=[[],[],[]]
  for t in prf:
    if t[6] != 1:
      if t[6] == -1:
        w[0].append(log10(t[3]))
        w[1].append(t[-2])
        w[2].append(t[-1])
      elif t[6] < -1:
        v[0].append(log10(t[3]))
        v[1].append(t[-2])
        v[2].append(t[-1])
      elif t[3] > 2.:  # 2MASS switch, ignore data inside 2"
        s[0].append(log10(t[3]))
        s[1].append(t[-2])
        s[2].append(t[-1])
  ymin=min(s[1]+s[2])
  ymax=max(s[1]+s[2])
  ymin=ymin-0.10*(ymax-ymin)
  ymax=ymax+0.10*(ymax-ymin)
  ax4.axis([xmin,xmax,ymin,ymax])
# blue is a_4, green is a_3
  ax4.scatter(s[0],s[1],s=75,marker=(4,2,pi/4.),color='b')
  ax4.scatter(s[0],s[2],s=75,marker=(4,2,pi/4.),color='g')
  ylabel('$A_3:A_4$')
  ax4.set_xlim(xmin,xmax)
  ax4.set_ylim(ymin,ymax)

  for ax in ax2,ax3,ax4:
    for label in ax.get_xticklabels():
      label.set_visible(False)

  a = axes([.50,.69,.3,.3]) #left, bottom, width, height
  ticklabels = a.get_xticklabels()
  for label in ticklabels:
    label.set_fontsize(9)
  ticklabels = a.get_yticklabels()
  for label in ticklabels:
    label.set_fontsize(9)
  gray()
  xc=int(prf[4][14])
  yc=int(prf[4][15])
  imshow(-fake[yc-50:yc+50,xc-50:xc+50],vmin=-prf[10][0],vmax=-r2,aspect='equal',origin='lower',interpolation='nearest')
  for label in a.get_yticklabels():
    label.set_visible(False)

  try:
    a = axes([.20,.69,.3,.3]) #left, bottom, width, height
    ticklabels = a.get_xticklabels()
    for label in ticklabels:
      label.set_fontsize(9)
    ticklabels = a.get_yticklabels()
    for label in ticklabels:
      label.set_fontsize(9)
    gray()
    xc=int(prf[4][14])
    yc=int(prf[4][15])
    imshow(-fake[yc-50:yc+50,xc-50:xc+50],vmin=-10.*r1,vmax=-r2,aspect='equal',origin='lower',interpolation='nearest')
  except:
    print 'no fake file'

  fig.savefig('pick.pdf')
#  ion()

if __name__ == '__main__':

  if sys.argv[1] == '-h':
    print help()
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

  else:
    print sys.argv[-1],'XML file not found - aborting'
    sys.exit()

  if os.path.exists(sys.argv[-1].split('.')[0]+'.fits'):
    fitsobj=pyfits.open(sys.argv[-1].split('.')[0]+'.fits',"readonly")
    pix=fitsobj[0].data
    fitsobj.close()
    sky=float(elements['sky'][0][1])
    skysig=float(elements['skysig'][0][1])
    r1=sky+50.*skysig
    r2=sky-0.05*(r1-sky)

  if os.path.exists(sys.argv[-1].split('.')[0]+'.fake'):
    fitsobj=pyfits.open(sys.argv[-1].split('.')[0]+'.fake',"readonly")
    fake=fitsobj[0].data
    fitsobj.close()

  if 'prometheus' in os.uname()[1]:
    fig = figure(figsize=(12, 16), dpi=80)  # initialize plot parameters
#    ax = fig.subplot(111)  # assign ax for text and axes
    manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager.window.title('')
    manager.window.geometry('+200+100') # move the window for deepcore big screen
  else:
    fig = figure(figsize=(9, 9), dpi=80)  # initialize plot parameters
#    ax = fig.subplot(111)  # assign ax for text and axes
    manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager.window.title('')
    manager.window.geometry('+400+50')

  r=[] ; s=[]
  for t in data:
    r.append(log10(t[0]))
  xmin=min(r)-0.10*(max(r)-min(r))
  xmax=max(r)+0.10*(max(r)-min(r))
  ymin=+0.5 ; ymax=-0.5

  draw_plot(False)
  if '-hard' in sys.argv: sys.exit()
  cid=connect('key_press_event',clicker)
  show()
