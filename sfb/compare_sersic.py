#!/usr/bin/env python

# warning, note 2MASS switch, no plot inside 2"

import sys, time, subprocess
from math import *
from xml_archangel import *
from pylab import *
from matplotlib.ticker import MultipleLocator
import pyfits

def clicker(event):
  global xmin,xmax,ymin,ymax,data,fig,ax,a_new
  global cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge,mu_err,mu_low,mu_high,lower_fit,upper_fit

  if event.key == '/':
    disconnect(cid)
    close('all')
    time.sleep(0.5)
    sys.exit()

  if event.key == 'h':
    fig.set_size_inches((8,8))
    draw_plot(True)
    fig.savefig('compare.pdf')

  draw_plot(False)

def draw_plot(usetex):
  global xmin,xmax,ymin,ymax,data,fig,ax,a_new
  global cstore,sstore,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge,mu_err,mu_low,mu_high,lower_fit,upper_fit

  clf()
  rc('text',usetex=True)

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

    xd=(xmax-xmin)/20.
    t1=[] ; t2=[]
    b=2.*n_sersic-(1./3.)
    xstep=xmax/300.
    for i in range(301):
      t=i*xstep+xmin+xd
      t1.append(t)
      t2.append(se_sersic+(2.5*b)*((10.**t/re_sersic)**(1./n_sersic)-1.)/log(10.))
    ax1 = fig.add_axes([0.10,0.10,0.80,0.80]) #left, bottom, width, height
    ax1.axis([xmin,xmax,ymax,ymin])
    ax1.plot(t1,t2,'b-')

    t1=[] ; t3=[]
    b=2.*a_new[2]-(1./3.)
    xstep=xmax/300.
    for i in range(301):
      t=i*xstep+xmin+xd
      t1.append(t)
      t3.append(a_new[0]+(2.5*b)*((10.**t/a_new[1])**(1./a_new[2])-1.)/log(10.))
    ax1.plot(t1,t3,'r-')

#    for t1,t2 in zip(r,s):
#      print t1,t2-(a_new[0]+(2.5*b)*((10.**t1/a_new[1])**(1./a_new[2])-1.)/log(10.))

    if '-d' in sys.argv:
      print 'output to compare.tmp'
      file=open('compare.tmp','w')
      for d1,d2,d3 in zip(t1,t2,t3):
        file.write(str(d1)+' '+str(d2)+' '+str(d3)+'\n')
      file.close()

    ax1.scatter(r,s,s=75,marker=(4,0,0),color='k')
    if len(v) > 0: ax1.scatter(v,w,s=75,marker=(4,2,45.),color='r')
    for x,y,err in zip(r,s,e):
      if err > .1 and err < 1.0: errorbar(x,y,yerr=err,ecolor='k')

    for x,y in zip(r,s):
      if x > log10(lower_fit_sersic):
        text(log10(lower_fit_sersic),y+0.03*(ymax-ymin),'$\uparrow$',color='b', \
             horizontalalignment='center',verticalalignment='center')
        break

    for x,y in zip(r,s):
      if x > log10(lower_fit_dev):
        text(log10(lower_fit_dev),y+0.03*(ymax-ymin),'$\uparrow$',color='r', \
             horizontalalignment='center',verticalalignment='center')
        break

    for x,y in zip(r,s):
      if x > log10(upper_fit_sersic):
        text(log10(upper_fit_sersic),y+0.03*(ymax-ymin),'$\uparrow$',color='b', \
             horizontalalignment='center',verticalalignment='center')
        break

    ylabel('$\mu$')
    xlabel('log (a*b)$^{1/2}$ (arcsecs)')
    text(xmin+(xmax-xmin)/2.,ymin-0.05*(ymax-ymin),sys.argv[-1].split('_')[0],color='k')
    ax1.plot([0.,0.25],[ymax-0.15*(ymax-ymin),ymax-0.15*(ymax-ymin)],'b-')
    text(.3,ymax-0.14*(ymax-ymin),'$\\mu_e$ = '+('%5.1f' % se_sersic)+', $r_e$ = '+ \
        ('%5.1f' % re_sersic)+', $n$ = '+('%5.1f' % n_sersic))
    ax1.plot([0.,0.25],[ymax-0.10*(ymax-ymin),ymax-0.10*(ymax-ymin)],'r-')
    text(.3,ymax-0.09*(ymax-ymin),'$\\mu_e$ = '+('%5.1f' % a_new[0])+', $r_e$ = '+ \
        ('%5.1f' % a_new[1])+', $n$ = '+('%5.1f' % a_new[2]))
    ax1.set_xlim(xmin,xmax)
    ax1.set_ylim(ymax,ymin)
  except:
    raise

#  ion()
  draw()

if __name__ == '__main__':

  if '-h' in sys.argv:
    print 'compare_sersic se1 re1 n1 se2 re2 n2 gal_prefix'
    print
    print 'options: -s = use xml fit as one'
    print '         -d = dump fits'
    sys.exit()

  if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
    doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    try:
      lower_fit_sersic=float(elements['lower_fit_sersic'][0][1])
      lower_fit_dev=float(elements['lower_fit_dev'][0][1])
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
    fig = figure(figsize=(10, 10), dpi=80)  # initialize plot parameters
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

  
  if '-s' in sys.argv:
    a_new=[float(elements['se_sersic'][0][1]),float(elements['re_sersic'][0][1]), \
           float(elements['n_sersic'][0][1])]
    se_sersic=float(sys.argv[2])
    re_sersic=float(sys.argv[3])
    n_sersic=float(sys.argv[4])
  else:
    a_new=[float(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6])]
    se_sersic=float(sys.argv[1])
    re_sersic=float(sys.argv[2])
    n_sersic=float(sys.argv[3])
  
  draw_plot(False)
  cid=connect('key_press_event',clicker)
  show()
