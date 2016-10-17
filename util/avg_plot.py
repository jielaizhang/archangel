#!/usr/bin/env python

import sys,os,time
from math import *
from matplotlib import rc
from pylab import *
from matplotlib.ticker import MultipleLocator # needed to fix up minor ticks

def xits(x,err,xsig):
# this is new weighted average version, takes array err and assigns weight
# as sig=100.*err[i]/x[i], weight=1/sig**2, if sig > 1., else weight=1.
  xmean1=0. ; sig1=0.
  for tmp in x:
    xmean1=xmean1+tmp
  try:
    xmean1=xmean1/len(x)
  except:
    return 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'
  for tmp in x:
    sig1=sig1+(tmp-xmean1)**2
  try:
    sig1=(sig1/(len(x)-1))**0.5
  except:
    return 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'
  xmean2=xmean1 ; sig2=sig1
  xold=xmean2+0.001*sig2
  its=0
  while (xold != xmean2 and its < 100):
    xold=xmean2
    its+=1
    dumw=0. ; dumww=0.
    dum=0.
    npts=0
    for tmp,tmp2 in zip(x,err):
      if abs(tmp-xold) < xsig*sig2:
        npts+=1
        dum=dum+tmp
        if tmp2 > 1.: tmp2=1.
        dumw=dumw+tmp2*tmp
        dumww=dumww+tmp2
    try:
      xmean2=dum/npts
      xmean3=dumw/dumww
    except:
      return xmean1,sig1,'NaN','NaN','NaN',len(x),'NaN','NaN'
    dum=0.
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        dum=dum+(tmp-xmean2)**2
    try:
      sig2=(dum/(npts-1))**0.5
      if sig2 == 0.: return xmean1,sig1,xmean2,sig2,xmean3,len(x),npts,its
    except:
      return xmean1,sig1,'NaN','NaN','NaN',len(x),'NaN','NaN'
  return xmean1,sig1,xmean2,sig2,xmean3,len(x),npts,its

def ticks(xmin,xmax):
  r=abs(xmax-xmin)
  if r == 1: return 0.25
  r=round(r/(10.**int(math.log10(r))),9)
  for n in range(0,-10,-1):
    if int(round(r/(10.**(n)),1))//((r/(10.**(n)))) == 1: break

  if int(round(r/(10.**(n)),1)) in [1,5]:
    return (r/5.)*(10.**int(math.log10(abs(xmax-xmin))))
  elif int(round(r/(10.**(n)),1)) in [2,4,8]:
    return (r/4.)*(10.**int(math.log10(abs(xmax-xmin))))
  elif int(round(r/(10.**(n)),1)) in [3,6,9]:
    return (r/3.)*(10.**int(math.log10(abs(xmax-xmin))))
  elif int(round(r/(10.**(n)),1)) == 7:
    return (r/7.)*(10.**int(math.log10(abs(xmax-xmin))))

def draw_x(usetex):
  global switch,xmin,xmax,ymin,ymax,smin,smax,axe

  clf() ; axe = fig.add_subplot(111)
  rc('text',usetex=usetex)

  axe.scatter(x,y,s=50.,marker=(6,2,0),color='b')
  for w,v,u in zip(x,y,bars):
    axe.errorbar(w,v,yerr=u,ecolor='r')
  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymin,ymax)

  tick=ticks(axe.xaxis.get_majorticklocs()[0],axe.xaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  axe.xaxis.set_minor_locator(minorLocator)
  tick=ticks(axe.yaxis.get_majorticklocs()[0],axe.yaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  axe.yaxis.set_minor_locator(minorLocator)

  if smin != xmin:
    t=[] ; z=[]
    for v,w,s in zip(x,y,err):
      if v >= smin and v <= smax: 
        t.append(w)
        z.append(s)
    figtext(0.20,0.88,'%.2f' % xits(t,z,2.5)[2], \
            horizontalalignment='left',verticalalignment='top',color='r',size=14)
    figtext(0.25,0.88,'%.2f' % xits(t,z,2.5)[3], \
            horizontalalignment='left',verticalalignment='top',color='r',size=14)
    figtext(0.30,0.88,'%.2f' % xits(t,z,2.5)[4], \
            horizontalalignment='left',verticalalignment='top',color='r',size=14)
    plot([smin,smin],[ymin,ymax],'c-')
    plot([smax,smax],[ymin,ymax],'g-')

  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymin,ymax)
  draw()

def clicker(event): # primary event handler
  global switch,xmin,xmax,ymin,ymax,smin,smax,axe

  cmd=event.key

  if event.key in ['/','q']:
    t=[] ; z=[]
    for v,w,s in zip(x,y,err):
      if v >= smin and v <= smax:
        t.append(w)
        z.append(s)
    file=open('avg_plot.tmp','a')
    file.write(sys.argv[-1]+' ')
    file.write('%.2f' % xits(t,z,2.5)[2]+' ')
    file.write('%.2f' % xits(t,z,2.5)[3]+' ')
    file.write('%.2f' % xits(t,z,2.5)[4])
    file.write('\n')
    file.close()
    disconnect(cid1)
    close('all')
    time.sleep(0.5)
    sys.exit()

  elif event.key == ',':
    smin=event.xdata

  elif event.key == '.':
    smax=event.xdata

  elif event.key == 'B': # interactive set border
    try:
      switch
      xmax=event.xdata
      ymax=event.ydata
      del(switch)
    except:
      switch=1
      xmin=event.xdata
      ymin=event.ydata

  if event.key not in ['shift']:
    draw_x(False)

#main

lines=[(map(float, tmp.split())) for tmp in open(sys.argv[1],'r').readlines()]

x=[] ; y=[] ; err=[] ; bars=[] ; xmin=ymin=1.e33 ; xmax=ymax=-1.e33
for line in lines:
  if 'nan' in line: continue
  x.append(line[0])
  y.append(line[1]) 
  if '-noerr' in sys.argv:
    bars.append(1.)
  else:
    bars.append(line[2])
  if line[0] > xmax: xmax=line[0]
  if line[0] < xmin: xmin=line[0]
  if line[1] > ymax: ymax=line[1]
  if line[1] < ymin: ymin=line[1]

for t1,t2 in zip(y,bars):
  err.append(1./(100.*(t2/t1)))

xmin=xmin-0.10*(xmax-xmin)
xmax=xmax+0.10*(xmax-xmin)
ymin=ymin-0.10*(ymax-ymin)
ymax=ymax+0.10*(ymax-ymin)
smin=xmin
smax=xmax
switch=0

geo=eval(' '.join([tmp[:-1] for tmp in open(os.environ['ARCHANGEL_HOME']+'/.archangel','r').readlines()]))
fig_size=int(geo['main_size'])

fig = figure(figsize=(fig_size, fig_size), dpi=80)  # initialize plot parameters
axe = fig.add_subplot(111)  # assign axe for text and axes
manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
manager.window.title('')
manager.window.geometry(geo['main_window'])

draw_x(False)

cid1=connect('key_press_event',clicker)
show()
