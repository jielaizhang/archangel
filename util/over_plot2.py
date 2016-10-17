#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import sys,os
from matplotlib import rc
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

fig, ax = plt.subplots()

axes = [ax, ax.twinx()]
files=['tmp.1','tmp.2']
#axes = [ax, ax, ax]

for file,ax in zip(files,axes):
    data = [(map(float, tmp.split())) for tmp in open(file,'r').readlines()]
    x=[] ; y=[]
    for z,t in data:
      x.append(z) ; y.append(t)
    if file in ['tmp.1']:
      ax.plot(x,y, marker='o', linestyle='none')
      ax.set_ylim(0.,5.)
      ax.set_ylabel('test')
      ax.tick_params(axis='y',          # changes apply to the x-axis
                   which='both',      # both major and minor ticks are affected
                   left='off',      # ticks along the bottom edge are off
                   right='off',         # ticks along the top edge are off
                   labelright='off') # labels along the bottom edge are off
    else:
      ax.plot(x,y, marker='x', linestyle='none')
      ax.set_ylim(0.,5.)
      ax.tick_params(axis='y',          # changes apply to the x-axis
                   which='both',      # both major and minor ticks are affected
                   left='on',      # ticks along the bottom edge are off
                   right='on',         # ticks along the top edge are off
                   labelright='off') # labels along the bottom edge are off
axes[0].set_xlabel('X-axis')

plt.show()
