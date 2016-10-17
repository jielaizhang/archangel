#!/usr/bin/env python

import sys, os.path, time, subprocess
import astropy.io.fits as pyfits
from pylab import *
from matplotlib.ticker import MultipleLocator
from matfunc import *
from xml.dom import minidom, Node
from xml_archangel import *
from matplotlib.patches import Ellipse
import warnings ; warnings.simplefilter('ignore')

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

def plot_asym():
  global axe,xmin,xmax,ymin,ymax,data1,data2,cmd,line,ft,cid1,cid2,imin,pix,r1,r2,prf,igray
  global mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,iasym,sky,half,half_r,fit_max,fit_min,zpt1,zpt2

  clf() ; axe = fig.add_subplot(111) ; asym=0.

  axis([xmin,xmax,ymin,ymax])
  xlabel('log r')
  ylabel('color')
  suptitle(sys.argv[-1].split('_')[0])

#  ioff()

# mark start point for exp addition
  axe.scatter([data1[imin][0]],[data1[imin][1]-data2[imin][1]],s=250,marker=(4,0,0),color='g')
  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymin,ymax)

# plot prf fitted datapoints, in blue, after start point, column 4
  x=[] ; lum=[] ; iplot=0
  for tmp in zip(data1[:imin+1],data2[:imin+1]): # use raw up to start point
    if tmp[0][2]:
      iplot=iplot+1 # only plot blue circles after start point
      x.append(tmp[0][0])
      lum.append(tmp[0][1]-tmp[1][1])
  if iplot < len(x)+1: iplot=1
  xlum1=10.**((data1[imin][1]-zpt1)/-2.5)
  xlum2=10.**((data2[imin][1]-zpt2)/-2.5)
  for tmp in zip(data1[imin+1:],data2[imin+1:]):
    if str(tmp[0][4]) != 'nan':
      xlum1=xlum1+10.**(tmp[0][4]/-2.5)
      xlum2=xlum2+10.**(tmp[1][4]/-2.5)
      x.append(tmp[0][0])
      lum.append((-2.5*math.log10(xlum1)+zpt1)-(-2.5*math.log10(xlum2)+zpt2))
  axe.scatter(x[iplot:],lum[iplot:],s=75,marker='8',edgecolor='b',facecolor='w')
  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymin,ymax)

# plot raw photometry datapoints, plot last to be on top
  x=[] ; y=[] ; last=0. ; isw=0
  for tmp in zip(data1,data2):
    if not isw and tmp[0][1] >= last:
      isw=1
    if not tmp[0][2] or isw:
      x.append(tmp[0][0])
      y.append(tmp[0][1]-tmp[1][1])
    last=tmp[0][1]-tmp[1][1]
  axe.scatter(x,y,s=50,marker=(6,2,0),color='r')
  x=[] ; y=[] ; last=1.e33
  for tmp in zip(data1[1:],data2[1:]):
#    if tmp[1] >= last: break
    if tmp[0][2]:
      x.append(tmp[0][0])
      y.append(tmp[0][1]-tmp[1][1])
    last=tmp[0][1]-tmp[1][1]
  axe.scatter(x,y,s=50,marker=(6,2,0),color='k')
  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymin,ymax)

#  ion()
  draw()
  return

def get_data():
  global axe,xmin,xmax,ymin,ymax,data1,data2,cmd,line,ft,cid1,cid2,imin,pix,r1,r2,prf,igray
  global mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,iasym,sky,half,half_r,fit_max,fit_min,zpt1,zpt2
  global x0,up,down,zpt,scale

  try:
    for root, dirs, files in os.walk('.'):
      for name in files:
        if 'xml' not in name: continue
        if sys.argv[-2] in name:
          raise
    else:
      print file,'no file found'
      sys.exit()
  except:
    pass

  try:
    doc = minidom.parse(root+'/'+name.split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)
  except:
    print sys.argv[-2].split('_'),'fail'
    sys.exit()

  try:
    scale=float(elements['scale'][0][1])
  except:
    print 'pixel scale value not found, setting to one'
    scale=1.
  try:
    zpt1=float(elements['zeropoint'][0][1])
  except:
    print 'zeropoint not found, setting to 25.'
    zpt1=25.
  try:
    exptime=float(elements['exptime'][0][1])
  except:
    exptime=1.
  if exptime != 0.:
    try:
      k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05}
      airmass=k[elements['filter'][0][1]]*float(elements['airmass'][0][1])
    except:
      airmass=0.
    zpt1=2.5*math.log10(exptime)-airmass+zpt1

  try:
    for t in elements['array']:
      if t[0]['name'] == 'prf':
        prf=[]
        for z in t[2]['axis']:
          prf.append(map(float,z[1].split('\n')))
        tmp=array(prf)
        prf=swapaxes(tmp,1,0)
        break
    else:
      print 'no prf data in .xml file - aborting'
      sys.exit()
  except:
    raise
    print 'problem with data in .xml file - aborting'
    sys.exit()

  try:
    for t in elements['array']:
      if t[0]['name'] == 'ept':
        pts=[]
        for z in t[2]['axis']:
          pts.append(map(float,z[1].split('\n')))
        tmp=array(pts)
        pts=swapaxes(tmp,1,0)
        break
    else:
      print 'no ept data in .xml file - aborting'
      sys.exit()
  except:
    raise
    print 'problem with data in .xml file - aborting'
    sys.exit()

  iter_pt=float(elements['tot_mag_iter_pt'][0][1])

  try:
    for imin,z in enumerate(pts):
      if round(scale*z[0],2) >= float(elements['tot_mag_iter_pt'][0][1]):
        xmn=round(scale*z[0],2)
        break
  except:
    for imin,z in enumerate(prf):
      if z[0]-sky < (prf[0][0]-sky)/100.: break
    xmn=round(z[3],2)

# storing log r (arcsecs), app mag, erase flag, number of pixels (for
# error), prf intensity, exp intensity

  data1=[]
  for n,line in enumerate(pts):
    t=math.log10(scale*line[0])
    data1.append([t,
                 line[1]+zpt1,
                 1,
                 line[2],
                 line[3],
                 line[4]])
    if round(line[0],2) == xmn: imin=n

  try:
    for root, dirs, files in os.walk('.'):
      for name in files:
        if 'xml' not in name: continue
        if sys.argv[-1] in name:
          raise
    else:
      print file,'no file found'
      sys.exit()
  except:
    pass

  doc = minidom.parse(root+'/'+name.split('.')[0]+'.xml')
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)

  try:
    scale=float(elements['scale'][0][1])
  except:
    print 'pixel scale value not found, setting to one'
    scale=1.
  try:
    zpt2=float(elements['zeropoint'][0][1])
  except:
    print 'zeropoint not found, setting to 25.'
    zpt2=25.
  try:
    exptime=float(elements['exptime'][0][1])
  except:
    exptime=1.
  if exptime != 0.:
    try:
      k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05}
      airmass=k[elements['filter'][0][1]]*float(elements['airmass'][0][1])
    except:
      airmass=0.
    zpt2=2.5*math.log10(exptime)-airmass+zpt2

  try:
    for t in elements['array']:
      if t[0]['name'] == 'prf':
        prf=[]
        for z in t[2]['axis']:
          prf.append(map(float,z[1].split('\n')))
        tmp=array(prf)
        prf=swapaxes(tmp,1,0)
        break
    else:
      print 'no prf data in .xml file - aborting'
      sys.exit()
  except:
    raise
    print 'problem with data in .xml file - aborting'
    sys.exit()

  try:
    for t in elements['array']:
      if t[0]['name'] == 'ept':
        pts=[]
        for z in t[2]['axis']:
          pts.append(map(float,z[1].split('\n')))
        tmp=array(pts)
        pts=swapaxes(tmp,1,0)
        break
    else:
      print 'no ept data in .xml file - aborting'
      sys.exit()
  except:
    raise
    print 'problem with data in .xml file - aborting'
    sys.exit()

# storing log r (arcsecs), app mag, erase flag, number of pixels (for
# error), prf intensity, exp intensity

  data2=[]
  for n,line in enumerate(pts):
    erase=1
    t=math.log10(scale*line[0])
    data2.append([t,
                 line[1]+zpt2,
                 1,
                 line[2],
                 line[3],
                 line[4]])
    if round(line[0],2) == xmn: imin=n

  if '-x' in sys.argv:
    last=data2[0]
    for t in data2[1:]:
      if t[0] > data1[imin][0]:
        print sys.argv[-1].split('_')[0],data1[imin][1]-interp(last[0],t[0],last[1],t[1],data1[imin][0])
        break
      last=t
    sys.exit()

  x=[] ; y=[]
  for tmp in zip(data1,data2):
    x.append(tmp[0][0])
    y.append(tmp[0][1]-tmp[1][1])
  xmin=min(x)-0.10*(max(x)-min(x))
  xmax=max(x)+0.10*(max(x)-min(x))
  ymin=min(y)-0.10*(max(y)-min(y))
  ymax=max(y)+0.10*(max(y)-min(y))

  return

def get_string(event): # event routine to get strings
  global axe,xmin,xmax,ymin,ymax,data1,data2,cmd,line,ft,cid1,cid2,imin,pix,r1,r2,prf,igray
  global mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,iasym,sky,half_half_r,fit_max,fit_min,zpt1,zpt2

  if event.key == 'enter': # <cr> disconnect, reconnect primary clicker, do action
    disconnect(cid2)
    action()
    plot_asym()
    cid1=connect('key_press_event',clicker)

  elif event.key == 'backspace': # delete characters, stop at 0 or ': '
    try:
      if line[-2:] != ': ': line=line[:-1]
    except:
      pass

  elif event.key in [None,'shift','control','alt','right','left','up','down','escape']: # ignore weird keys
    pass

  else:
    line=line+event.key

  try:
    fig.texts.remove(ft) # remove the line for redraw
  except:
    pass

  ft=figtext(0.1,0.05,line,horizontalalignment='left',verticalalignment='top')

def action(): # do the actions from clicker as given by var cmd
  global axe,xmin,xmax,ymin,ymax,data1,data2,cmd,line,ft,cid1,cid2,imin,pix,r1,r2,prf,igray
  global mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,iasym,sky,half,half_r,fit_max,fit_min,zpt1,zpt2

  try:
    if cmd == 'b': # do borders
      xmin=float(line.split(': ')[-1].split()[0])
      xmax=float(line.split(': ')[-1].split()[1])
      if float(line.split(': ')[-1].split()[2]) > float(line.split(': ')[-1].split()[3]):
        ymax=float(line.split(': ')[-1].split()[2])
        ymin=float(line.split(': ')[-1].split()[3])
      else:
        ymin=float(line.split(': ')[-1].split()[2])
        ymax=float(line.split(': ')[-1].split()[3])
    if cmd == 's': # new sky
      sky=float(line.split(': ')[-1])
      os.system('el -b -sky '+str(sky)+' '+sys.argv[-1])
      get_data()
  except:
    fig.texts.remove(ft)
    ft=figtext(0.1,0.05,'INPUT ERROR',horizontalalignment='left',verticalalignment='top',color='r')
    time.sleep(2)
  line=''
  return

def clicker(event):
  global axe,xmin,xmax,ymin,ymax,data1,data2,cmd,line,ft,cid1,cid2,imin,pix,r1,r2,prf,igray
  global mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,iasym,sky,half,half_r,fit_max,fit_min,zpt1,zpt2

  cmd=event.key

  if event.key in ['/','q']:
    disconnect(cid1)
    close('all')
    time.sleep(0.5)
    sys.exit()

# set the iter point (z-point), where the sfb and fit are started
  if event.key == 'z':
    rmin=1.e33
    for tmp in data1:
      n=data1.index(tmp)
      try:
        rr=abs(event.xdata-tmp[0])
        if rr <= rmin:
          rmin=rr
          imin=n
      except:
        break

  if event.key == 'b': line='Enter xmin,xmax,ymin,ymax: '

  if event.key in ['1','2','3','4','x',',','.']:
    if event.key == '.': fit_max=event.xdata
    if event.key == ',': fit_min=event.xdata
    if event.key in ['.',',']:
      for n,tmp in enumerate(data1):
        if tmp[0] >= fit_min and tmp[0] <= fit_max:
          data1[n][2]=1
        else:
          data1[n][2]=0
    else:
      rmin=1.e33
      for n,tmp in enumerate(data1):
        rr=(((event.xdata-tmp[0])/(xmax-xmin))**2+((event.ydata-tmp[1])/(ymax-ymin))**2)**0.5
        if rr <= rmin:
          rmin=rr
          dmin=n
        if cmd == '1' and tmp[0] > event.xdata and tmp[1] > event.ydata: data1[n][2]=abs(data1[n][2]-1)
        if cmd == '2' and tmp[0] < event.xdata and tmp[1] > event.ydata: data1[n][2]=abs(data1[n][2]-1)
        if cmd == '3' and tmp[0] < event.xdata and tmp[1] < event.ydata: data1[n][2]=abs(data1[n][2]-1)
        if cmd == '4' and tmp[0] > event.xdata and tmp[1] < event.ydata: data1[n][2]=abs(data1[n][2]-1)
      if cmd == 'x': data1[dmin][2]=abs(data1[dmin][2]-1)

  if event.key in ['r','b','s']:
    ft=figtext(0.1,0.05,line,horizontalalignment='left',verticalalignment='top')
    disconnect(cid1)
    cid2=connect('key_press_event',get_string)
  elif event.key not in [None,'shift','control','alt','right','left','up','down','escape']:
    plot_asym()

if __name__ == '__main__':

  if '-h' in sys.argv:
    print 'Usage: total_color file1 file2'
    print
    print 'options: -ext = use galactic extinction'
    print
    print 'cursor commands:'
    print
    print 'r = reset                  z = set profile extrapolation point'
    print
    print 'x,1,2,3,4 = delete points'
    print ', = kill below             . = kill above'
    print
    print 'b = change borders'
    print 'q,/ = exit'
    sys.exit()

  get_data()

  geo=eval(' '.join([tmp[:-1] for tmp in open(os.environ['ARCHANGEL_HOME']+'/.archangel','r').readlines()]))
  if 'prometheus' in os.uname()[1]:
    fig = figure(figsize=(12, 12), dpi=80)  # initialize plot parameters
    axe = fig.add_subplot(111)  # assign axe for text and axes
    manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager.window.title('')
    manager.window.geometry('+1200+300') # move the window for deepcore big screen
  else:
    fig = figure(figsize=(9, 9), dpi=80)  # initialize plot parameters
    axe = fig.add_subplot(111)  # assign axe for text and axes
    manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager.window.title('')
#  manager.window.geometry('+400+50')
    manager.window.geometry(geo['main_window'])

  line='' ; cmd=''

  plot_asym()

  cid1=connect('key_press_event',clicker)
  show()
