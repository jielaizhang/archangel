#!/usr/bin/env python

import sys,os,time,subprocess,signal
import astropy.io.fits as pyfits
from math import *
from xml_archangel import *
from pylab import *
from matplotlib.ticker import MultipleLocator # needed to fix up minor ticks
from matplotlib.patches import Ellipse, Polygon

def get_data():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,inv

  try: # test for file existance and get header information
    fitsobj=pyfits.open(sys.argv[-1],"readonly")
  except:
    print filename,'not found -- ABORTING'
    return
  nx=fitsobj[0].header['NAXIS1']
  ny=fitsobj[0].header['NAXIS2']
  hdr=fitsobj[0].header
  pix=fitsobj[0].data # read the pixels
  fitsobj.close()

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

def draw_image():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,inv

  matplotlib.rcParams['xtick.direction'] = 'out'
  matplotlib.rcParams['ytick.direction'] = 'out'
  cs=contour(pix)
  clabel(cs, inline=1, fontsize=10)
  draw()

def clicker(event): # primary event handler
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,inv

  if event.key in ['/','q']:
    sys.exit()

  draw_image()

# main

get_data()

geo=eval(' '.join([tmp[:-1] for tmp in open(os.environ['ARCHANGEL_HOME']+'/.archangel','r').readlines()]))

fig_size=int(geo['main_size'])
plt = figure(figsize=(fig_size, fig_size), dpi=80)
try:
  manager = get_current_fig_manager()
  manager.window.title('')
  manager.window.geometry(geo['main_window'])
except:
  pass

draw_image()
cid=connect('key_press_event',clicker)
show()
