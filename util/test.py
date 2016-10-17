#!/usr/bin/env python

import sys,os,time
from math import *
from pylab import *
from matplotlib.ticker import MultipleLocator # needed to fix up minor ticks

def clicker(event): # primary event handler
  print 'key',event.key
  if event.key == 'l':
    axe.set_xscale('linear') ; axe.set_yscale('linear') ; draw()
  if event.key == 'g':
    axe.grid(False) ; draw()
  if event.key == '/': sys.exit()

fig = figure(figsize=(12, 12), dpi=80)  # initialize plot parameters
axe = fig.add_subplot(111)  # assign axe for text and axes
axis([1.,2.,1.,2.])
cid1=connect('key_press_event',clicker)
show()
