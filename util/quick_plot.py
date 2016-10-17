#!/usr/bin/env python

import sys,os,time,subprocess
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
  global switch,xmin,xmax,ymin,ymax

  ioff()
  clf() ; axe = fig.add_subplot(111)
  rc('text',usetex=usetex)

  axe.scatter(x,y,s=50.,marker=(6,2,0),color='k')
  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymin,ymax)

  tick=ticks(axe.xaxis.get_majorticklocs()[0],axe.xaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  axe.xaxis.set_minor_locator(minorLocator)
  tick=ticks(axe.yaxis.get_majorticklocs()[0],axe.yaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  axe.yaxis.set_minor_locator(minorLocator)

  ion()
  draw()

def clicker(event): # primary event handler
  global switch,xmin,xmax,ymin,ymax

  cmd=event.key

  ioff()

  if event.key in ['/','q']:
    disconnect(cid1)
    close('all')
    time.sleep(0.5)
    sys.exit()

  elif event.key == 'B': # interactive set border
    try:
      print 'in'
      switch
      xmax=event.xdata
      ymax=event.ydata
      del(switch)
    except:
      print 'out'
      switch=1
      xmin=event.xdata
      ymin=event.ydata

  ion()

  if event.key not in ['shift']:
    draw_x(False)

#main

try:
  i=int(sys.argv[-2])
  j=int(sys.argv[-1])
except:
  i=0
  j=1

x=[] ; y=[] ; xmin=ymin=1.e33 ; xmax=ymax=-1.e33
file=open(sys.argv[1],'r')
while 1:
  line=file.readline()
  if not line: break
  x.append(float(line.split()[i]))
  y.append(float(line.split()[j]))
  if float(line.split()[i]) > xmax: xmax=float(line.split()[i])
  if float(line.split()[j]) > ymax: ymax=float(line.split()[j])
  if float(line.split()[i]) < xmin: xmin=float(line.split()[i])
  if float(line.split()[j]) < ymin: ymin=float(line.split()[j])
file.close()
xmin=xmin-0.10*(xmax-xmin)
xmax=xmax+0.10*(xmax-xmin)
ymin=ymin-0.10*(ymax-ymin)
ymax=ymax+0.10*(ymax-ymin)

from Tkinter import Tk
w=Tk()
s_width=w.winfo_screenwidth()
s_height=w.winfo_screenheight()
w.destroy()

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
