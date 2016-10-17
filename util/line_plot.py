#!/usr/bin/env python

import sys,os,time
from math import *
from matplotlib import rc
from pylab import *
from matplotlib.ticker import MultipleLocator # needed to fix up minor ticks

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
  global switch,xmin,xmax,ymin,ymax,smin,smax,axe,ifile

  clf() ; axe = fig.add_subplot(111)
  rc('text',usetex=usetex)

  colors=['k','r','b','g','m']
  icol=-1
  if '-single' in sys.argv:
    coords=data[ifile]
    x=[] ; y=[]
    for r,s in coords:
      x.append(r) ; y.append(s)
    axe.plot(x,y,'b-')
    text(xmin+0.1*(xmax-xmin),ymax-0.1*(ymax-ymin),files[ifile], \
            horizontalalignment='left',verticalalignment='top',color='k',size=14)
    axe.set_xlim(xmin,xmax)
    axe.set_ylim(ymin,ymax)
  else:
    for coords in data:
      icol=icol+1
      if icol > 4: icol=0
      x=[] ; y=[]
      for r,s in coords:
        x.append(r) ; y.append(s)
      axe.plot(x,y,colors[icol]+'-')
      axe.set_xlim(xmin,xmax)
      axe.set_ylim(ymin,ymax)

  tick=ticks(axe.xaxis.get_majorticklocs()[0],axe.xaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  axe.xaxis.set_minor_locator(minorLocator)
  tick=ticks(axe.yaxis.get_majorticklocs()[0],axe.yaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  axe.yaxis.set_minor_locator(minorLocator)

  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymin,ymax)
  draw()

def clicker(event): # primary event handler
  global switch,xmin,xmax,ymin,ymax,smin,smax,axe,ifile

  cmd=event.key

  if event.key in ['/','q']:
    disconnect(cid1)
    close('all')
    time.sleep(0.5)
    sys.exit()

  elif event.key == 'b':
    ifile=ifile-1
    if ifile < 0: ifile=len(data)

  elif event.key == 'n':
    ifile=ifile+1
    if ifile > len(data): ifile=0

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

if '-h' in sys.argv:
  print 'line_plot list_of_files'
  print
  print 'plots bunch of fiels as lines (e.g., color gradients)'
  print
  print 'options: -single = plot each file at a time (hit n)'
  sys.exit()

files=[tmp[:-1] for tmp in open(sys.argv[-1],'r').readlines()]
ifile=0

data=[] ; xmin=ymin=1.e33 ; xmax=ymax=-1.e33
for file in files:
  lines=[tmp.split() for tmp in open(file,'r').readlines()]
  coords=[]
  for line in lines:
    if len(line) == 0: continue
    if 'nan' in line: continue
    r=float(line[0]) ; s=float(line[1])
    coords.append([r,s]) 
    if r > xmax: xmax=r
    if r < xmin: xmin=r
    if s > ymax: ymax=s
    if s < ymin: ymin=s
  data.append(coords)

if '-xy' not in sys.argv:
  xmin=xmin-0.10*(xmax-xmin)
  xmax=xmax+0.10*(xmax-xmin)
  ymin=ymin-0.10*(ymax-ymin)
  ymax=ymax+0.10*(ymax-ymin)
else:
  xmin=float(sys.argv[-5])
  xmax=float(sys.argv[-4])
  ymin=float(sys.argv[-3])
  ymax=float(sys.argv[-2])
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
