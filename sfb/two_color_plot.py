#!/usr/bin/env python

import sys, os.path, time, subprocess
import astropy.io.fits as pyfits
from math import *
from xml_archangel import *
from pylab import *
from matplotlib.ticker import MultipleLocator
import matplotlib.font_manager as font_manager

def help():
  return '''
Usage: sfb_plot options file_name

surface photometry plot, output to file_name_sfbplot.pdf

options: -h = this message
         -d = use r
         -e = use (a*b)^1/4
         -s = use log (a*b)
      -hard = only hardcopy'''

if __name__ == '__main__':

  if '-h' in sys.argv:
    print help()
    sys.exit()

  try:
    doc = minidom.parse(sys.argv[-2].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

# ifit = 0, all fits
# ifit = 1, disk only fit
#      = 2, r^1/4 only fit
#      = 3, B+D fit, hold central disk sfb
#      = 4, B+D fit, all four parameters
#      = 5, Sersic fit

    if '-d' in sys.argv:
      ifit=1

    if '-c' in sys.argv:
      ifit=6

    if '-b' in sys.argv:
      ifit=3

    if '-e' in sys.argv:
      ifit=2

    if '-s' in sys.argv or '-a' in sys.argv:
      if '-a' in sys.argv:
        ifit=0
      else:
        ifit=5

    try:
      blue_scale=float(elements['scale'][0][1])
    except:
      blue_scale=1.

    try:
      sky=float(elements['sky'][0][1])
    except:
      sky=0.
    try:
      skysig=float(elements['skysig'][0][1])
    except:
      skysig=1.
    isfb=0

    for t in elements['array']:
      if t[0]['name'] == 'prf':
        blue_prf=[]
        head=[]
        for z in t[2]['axis']:
          blue_prf.append(map(float,z[1].split('\n')))
          head.append(z[0]['name'])
        tmp=array(blue_prf)
        blue_prf=swapaxes(tmp,1,0)

      if t[0]['name'] == 'sfb' and sys.argv[1] != '-p':
        isfb=1
        blue_data=[]
        tmp=[]
        head=[]
        for z in t[2]['axis']:
          head.append(z[0]['name'])
          tmp.append(map(float,z[1].split('\n')))
        for z in range(len(tmp[0])):
          kill=int(tmp[head.index('kill')][z])
          try: # if errorbars in sfb area
            blue_data.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                         kill,tmp[head.index('error')][z]])
          except:
            blue_data.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                         kill,0.])
        break

  except:
    raise
    print sys.argv[-1],'XML error'
    sys.exit()

  try:
    doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    try:
      red_scale=float(elements['scale'][0][1])
    except:
      red_scale=1.

    isfb=0
    for t in elements['array']:
      if t[0]['name'] == 'prf':
        red_prf=[]
        head=[]
        for z in t[2]['axis']:
          red_prf.append(map(float,z[1].split('\n')))
          head.append(z[0]['name'])
        tmp=array(red_prf)
        red_prf=swapaxes(tmp,1,0)

      if t[0]['name'] == 'sfb' and sys.argv[1] != '-p':
        isfb=1
        red_data=[]
        tmp=[]
        head=[]
        for z in t[2]['axis']:
          head.append(z[0]['name'])
          tmp.append(map(float,z[1].split('\n')))
        for z in range(len(tmp[0])):
          kill=int(tmp[head.index('kill')][z])
          try: # if errorbars in sfb area
            red_data.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                         kill,tmp[head.index('error')][z]])
          except:
            red_data.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                         kill,0.])
        break

  except:
    raise
    print sys.argv[-1],'XML error'
    sys.exit()

  if os.path.exists(sys.argv[-2]+'.fits'):
    doc = minidom.parse(sys.argv[-2].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)
    fitsobj=pyfits.open(sys.argv[-2]+'.fits',"readonly")
    nx=fitsobj[0].header['NAXIS1']
    ny=fitsobj[0].header['NAXIS2']
    pix=fitsobj[0].data
    fitsobj.close()
    try:
      r1=float(elements['sfb_plot_contrast'][0][1].split()[0])
      middle=float(elements['sfb_plot_contrast'][0][1].split()[1])
      r2=float(elements['sfb_plot_contrast'][0][1].split()[2])
    except:
      r1=sky+50.*skysig
      r2=sky-0.05*(r1-sky)
      middle=sky
    try:
      i1=int(elements['sfb_plot_zoom'][0][1].split()[0])
      i2=int(elements['sfb_plot_zoom'][0][1].split()[1])
      j1=int(elements['sfb_plot_zoom'][0][1].split()[2])
      j2=int(elements['sfb_plot_zoom'][0][1].split()[3])
      xxstep=float(elements['sfb_plot_zoom'][0][1].split()[4])
    except:
      xxstep=nx/2
      i1=1
      i2=nx
      j1=1
      j2=ny
    grey=1
  else:
    grey=0

  fig = figure(figsize=(12, 12), dpi=80)  # initialize plot parameters
  manager = get_current_fig_manager()
  manager.window.title('')
  manager.window.geometry('+1200+300')

  rect1 = [0.10, 0.30, 0.80, 0.60]
  rect2 = [0.70, 0.70, 0.18, 0.18]
  rect3 = [0.10, 0.10, 0.80, 0.20]

  ax1 = fig.add_axes(rect1)  #left, bottom, width, height
  ax3  = fig.add_axes(rect3)

  for label in ax1.get_xticklabels():
    label.set_visible(False)

  if grey:
    ax2 = fig.add_axes(rect2)
    ax2.xaxis.set_ticklabels([None])
    ax2.yaxis.set_ticklabels([None])
    ax2.xaxis.set_ticks([None])
    ax2.yaxis.set_ticks([None])
    gray()
    zm=ma.masked_where(isnan(pix[j1-1:j2,i1-1:i2]), pix[j1-1:j2,i1-1:i2])
    ax2.imshow(-zm,vmin=-r1,vmax=-r2,extent=(i1-0.5,i2+0.5,j1-0.5,j2+0.5), \
               aspect='equal',origin='lower',interpolation='nearest')

  r1=[] ; s1=[] ; e1=[]
  for t in blue_data:
    if ifit in [0,2,5]:
      for y in blue_prf:
        if y[3]*blue_scale >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          break
    else:
      tmp=t[0]
    if t[2]:
      if ifit == 2:
        r1.append(tmp**0.25)
      elif ifit == 0:
        r1.append(log10(tmp))
      elif ifit == 5:
        r1.append(log10(tmp))
      else:
        r1.append(t[0])
      s1.append(t[1])
      e1.append(t[3])

  r2=[] ; s2=[] ; e2=[]
  for t in red_data:
    if ifit in [0,2,5]:
      for y in red_prf:
        if y[3]*red_scale >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          break
    else:
      tmp=t[0]
    if t[2]:
      if ifit == 2:
        r2.append(tmp**0.25)
      elif ifit == 0:
        r2.append(log10(tmp))
      elif ifit == 5:
        r2.append(log10(tmp))
      else:
        r2.append(t[0])
      s2.append(t[1])
      e2.append(t[3])

  xmin=min(min(r1),min(r2))
  xmax=max(max(r1),max(r2))

  xmin=xmin-0.05*(xmax-xmin)
  t=int(xmin) % 5
  xmin=int(xmin)-(5-t)

  xmax=xmax+0.10*(xmax-xmin)
  t=int(xmax) % 5
  xmax=int(xmax)+(5-t)

  ymin=min(min(s1),min(s2))
  ymax=max(max(s1),max(s2))

  ymin=ymin-0.10*(ymax-ymin)
  ymin=int(ymin)

  ymax=ymax+0.10*(ymax-ymin)
  ymax=int(ymax)+1.5

  ax1.scatter(r1,s1,s=75,marker=(4,0,0),facecolor='b',color='b')
  ax1.set_xlim(xmin,xmax)
  ax1.set_ylim(ymax,ymin)
  for x,y,err in zip(r1,s1,e1):
    if err > abs(ymax-ymin)/200. and err > .1: ax1.errorbar(x,y,yerr=err,ecolor='b')

  ax1.scatter(r2,s2,s=75,marker=(4,0,0),facecolor='r',color='r')
  ax1.set_xlim(xmin,xmax)
  ax1.set_ylim(ymax,ymin)
  for x,y,err in zip(r2,s2,e2):
    if err > abs(ymax-ymin)/200. and err > .1: ax1.errorbar(x,y,yerr=err,ecolor='r')

  color=os.popen('~/archangel/sfb/two_sfb_color.py '+sys.argv[-2]+' '+sys.argv[-1]).read().split('\n')

  x=[] ; y=[] ; f=[]
  for t in color[:-1]:
    if ifit in [0,2,5]:
      tmp=float(t.split()[0])
      for z in blue_prf:
        if z[3] >= tmp:
          tmp=(tmp*tmp*(1.-z[12]))**0.5
          break
    else:
      tmp=float(t.split()[0])
    if ifit == 2:
      x.append(tmp**0.25)
    elif ifit == 0:
      x.append(log10(tmp))
    elif ifit == 5:
      x.append(log10(tmp))
    else:
      x.append(tmp)
    y.append(float(t.split()[1]))
    f.append(float(t.split()[2]))

  ymin=min(y)
  ymax=max(y)

  ymin=ymin-0.10*(ymax-ymin)
  t=int(ymin)*10 % 5
  ymin=int(ymin*10)/10.-(.5-t)

  ymax=ymax+0.10*(ymax-ymin)
  t=int(ymax)*10 % 5
  ymax=int(ymax*10)/10.+(.5-t)

  ax3.scatter(x,y,s=75,marker=(4,0,0),facecolor='k',color='k')
  for v,w,err in zip(x,y,f):
    if err > abs(ymax-ymin)/200. and err > .2: ax3.errorbar(v,w,yerr=err,ecolor='k')
  ax3.set_xlim(xmin,xmax)
  ax3.set_ylim(ymin,ymax)

  ax1.set_title(sys.argv[-1].split('_')[0])
  ax1.set_ylabel('$\\mu$ (mag/arcsec$^{-2}$)')
  if ifit == 2:
    ax3.set_xlabel('r$^{1/4}$ (arcsecs)')
  elif ifit == 0:
    ax3.set_xlabel('log r (arcsecs)')
  elif ifit == 5:
    ax3.set_xlabel('log r (arcsecs)')
  else:
    ax3.set_xlabel('r (arcsecs)')

  f1=sys.argv[-2].split('_')[-1]
  f2=sys.argv[-1].split('_')[-1]
  if f2 == 'ch1': f2='3.6'
  ax3.set_ylabel(f1+' - '+f2)

  if '-hard' in sys.argv:
    fig.savefig(sys.argv[-1].split('_')[0]+'_twosfb.pdf')
  else:
    show()
