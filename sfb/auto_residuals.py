#!/usr/bin/env python

# warning, note 2MASS switch, no plot inside 2"

import sys, time, subprocess
from math import *
from xml_archangel import *
from pylab import *
from matplotlib.ticker import MultipleLocator
import pyfits

def clicker(event):
  global xmin,xmax,ymin,ymax,data,fig,ax
  global cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge,mu_err,mu_low,mu_high,lower_fit,upper_fit

  if event.key == '/':
    disconnect(cid)
    close('all')
    time.sleep(0.5)
    sys.exit()

  if event.key == 'b':
    line='0 1 2 3 4\nfit_min fit_max err mu_low mu_high\n8 8 6 6 6\n'
    line=line+str(lower_fit)+' '
    line=line+str(upper_fit)+' '
    line=line+str(mu_err)+' '
    line=line+str(mu_low)+' '
    line=line+str(mu_high)+'\n'
    
    p = subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -entry_field -noadd', \
                         shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=p.communicate(line)[0]
    lower_fit=float(tmp.split()[0])
    upper_fit=float(tmp.split()[1])
    mu_err=float(tmp.split()[2])
    mu_low=float(tmp.split()[3])
    mu_high=float(tmp.split()[4])

  if event.key == '.':
    upper_fit=10.**(float(event.xdata))

  if event.key in ['shift',',']:
    lower_fit=10.**(float(event.xdata))
  else:
    draw_plot(False)

def draw_plot(usetex):
  global xmin,xmax,ymin,ymax,data,fig,ax
  global cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge,mu_err,mu_low,mu_high,lower_fit,upper_fit

#  ioff()

  clf()
  rc('text',usetex=True)

  ymin=+0.5 ; ymax=-0.5
  suptitle(r'\rm '+sys.argv[-1].split('_')[0])
  yd=(ymax-ymin)/8.
  xd=(xmax-xmin)/40.

  try:
    r=[] ; s=[] ; v=[] ; w=[] ; e=[]
    cmd='~/archangel/sfb/auto_fit.py -s -x '+str(lower_fit)+' '+str(upper_fit)+' -err '+str(mu_err)+' '+sys.argv[-1]
    print cmd
    dum=os.popen(cmd).read().split()
    print 'auto_fit output',dum
    a_new=[float(dum[1]),float(dum[2]),float(dum[3])]
    for t in data:
      for y in prf:
        if y[3] >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          break
      else:
        tmp=(t[0]*t[0]*(1.-prf[-1][12]))**0.5
      b=2.*a_new[2]-(1./3.)
      xnt1=-2.5*log10((10.**(a_new[0]/-2.5))*exp(-b*((tmp/a_new[1])**(1./a_new[2])-1.)))
      if t[2]:
        r.append(log10(tmp)) ; s.append(t[1]-xnt1) ; e.append(t[3])
      else:
        v.append(log10(tmp)) ; w.append(t[1]-xnt1)
    ax4 = fig.add_axes([0.10,0.70,0.80,0.25]) #left, bottom, width, height
    ax4.axis([xmin,xmax,ymin,ymax])
    ax4.scatter(r,s,s=75,marker=(4,0,0),color='k')
    if len(v) > 0: ax4.scatter(v,w,s=75,marker=(4,2,pi/4.),color='r')
    ax4.plot([xmin,xmax],[0.,0.],'r-')
    for x,y,err in zip(r,s,e):
      if err > .1 and err < .4: errorbar(x,y,yerr=err,ecolor='k')
    text(xmin+xd,ymax-1.5*yd,'Sersic: $\\mu_e$ = '+('%5.2f' % float(dum[1]))+ \
                             ', $r_e$ = '+('%5.2f' % float(dum[2]))+ \
                             ', n = '+('%5.2f' % float(dum[3])),fontsize=12)
    text(log10(lower_fit),0.1,'$\uparrow$',color='g', \
         horizontalalignment='center',verticalalignment='center')
    text(log10(upper_fit),0.1,'$\uparrow$',color='g', \
         horizontalalignment='center',verticalalignment='center')
    text(xmin+5.*xd,ymin+yd/3.,'$\\chi^2$ = '+('%8.2e' % float(dum[4])),fontsize=12)
    ylabel('$\Delta\mu$')
    ax4.set_xlim(xmin,xmax)
    ax4.set_ylim(ymin,ymax)
  except:
    raise

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
        r.append(log10(tmp)) ; s.append(t[1]-xnt1) ; e.append(t[3])
      else:
        v.append(log10(tmp)) ; w.append(t[1]-xnt1)
    ax3 = fig.add_axes([0.10,0.45,0.80,0.25]) #left, bottom, width, height
    ax3.axis([xmin,xmax,ymin,ymax])
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
    text(xmin+5.*xd,ymin+yd/3.,'$\\chi^2$ = '+('%8.2e' % chisq_sersic),fontsize=12)
    ylabel('$\Delta\mu$')
    ax3.set_xlim(xmin,xmax)
    ax3.set_ylim(ymin,ymax)
  except:
    raise

  try:
    r=[] ; s=[] ; v=[] ; w=[] ; e=[]
    for t in data:
      for y in prf:
        if y[3] >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          break
      if t[2]:
        r.append(log10(tmp))
        s.append(t[1])
        e.append(t[3])
      else:
        v.append(log10(tmp))
        w.append(t[1])
    ymin=min(s)-0.10*(max(s)-min(s))
    ymax=max(s)+0.10*(max(s)-min(s))
    t1=[] ; t2=[]
    b=2.*n_sersic-(1./3.)
    xstep=xmax/300.
    for i in range(301):
      t=i*xstep+xmin+xd
      t1.append(t)
      t2.append(se_sersic+(2.5*b)*((10.**t/re_sersic)**(1./n_sersic)-1.)/log(10.))
    ax1 = fig.add_axes([0.10,0.05,0.80,0.40]) #left, bottom, width, height
    ax1.axis([xmin,xmax,ymax,ymin])
    ax1.plot(t1,t2,'b-')
    t1=[] ; t2=[]
    b=2.*a_new[2]-(1./3.)
    xstep=xmax/300.
    for i in range(301):
      t=i*xstep+xmin+xd
      t1.append(t)
      t2.append(a_new[0]+(2.5*b)*((10.**t/a_new[1])**(1./a_new[2])-1.)/log(10.))
    ax1.plot(t1,t2,'r-')
    ax1.scatter(r,s,s=75,marker=(4,0,0),color='k')
    if len(v) > 0: ax1.scatter(v,w,s=75,marker=(4,2,pi/4.),color='r')
    ax1.plot([xmin,xmax],[0.,0.],'b-')
    for x,y,err in zip(r,s,e):
      if err > .1 and err < 1.0: errorbar(x,y,yerr=err,ecolor='k')
    ylabel('$\mu$')
    xlabel('log (a*b)$^{1/2}$ (arcsecs)')
    ax1.set_xlim(xmin,xmax)
    ax1.set_ylim(ymax,ymin)
  except:
    raise

#  ion()
  draw()

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
      lower_fit=lower_fit_sersic
      upper_fit=upper_fit_sersic
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

  if 'prometheus' in os.uname()[1]:
    fig = figure(figsize=(10, 14), dpi=80)  # initialize plot parameters
#    ax = fig.subplot(111)  # assign ax for text and axes
    manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager.window.title('')
    manager.window.geometry('+1400+200') # move the window for deepcore big screen
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

  mu_err=2.
  mu_low=30.
  mu_high=12.

  draw_plot(False)
  cid=connect('key_press_event',clicker)
  show()
