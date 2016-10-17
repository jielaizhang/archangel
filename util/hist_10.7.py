#!/usr/bin/env python

# this is matplotlib version of the HIST program
# first attempt to port PGPLOT to matplotlib (dear god)

# note: several things changed in matplotlibrc to increase font/tick sizes

import sys,math,os
from pylab import *
import numpy
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

def xits(x,xsig):                      # clipping mean subroutine
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
    dum=0.
    npts=0
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        npts+=1
        dum=dum+tmp
    try:
      xmean2=dum/npts
    except:
      return xmean1,sig1,'NaN','NaN',len(x),'NaN','NaN'
    dum=0.
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        dum=dum+(tmp-xmean2)**2
    try:
      sig2=(dum/(npts-1))**0.5
    except:
      return xmean1,sig1,'NaN','NaN',len(x),'NaN','NaN'
  return xmean1,sig1,xmean2,sig2,len(x),npts,its

def draw_h(usetex): # main drawing routine, note the globals from clicker functions
  global xlow,xhi,ylow,yhi,xbin,line,colors,ft,cid1,cid2,raw,labels,cmd,norm,ax,scale

  if not usetex:
    clf()
    rc('text',usetex=usetex)

  nbin=int((xhi-xlow)/xbin) # initialize bins,yhi,colors
  a=[]
  icolor=-1
  yhi=0.
  ymax=[] ; xmax=[]
  xtot=[]

  if norm: # plot normalized histogram

    if norm == 2:
      for x in raw:
        bin=[]
        data=[]
        for i in range(nbin+2):
          bin.append(i*xbin-xbin/2.+xlow)
          data.append(0)
        for s in x:
          for w in range(len(bin)-1):
            if s >= bin[w] and s < bin[w+1]:
              data[w]=data[w]+1

        npts=0.
        stot=0.
        for r,s in zip(bin,data):
          if s == 0.: continue
          xsum=0.
          for w in x:
            z=(r-w)/(xbin/2.)
            xsum=xsum+math.exp(-0.5*z**2)
          stot=stot+s*s/xsum
          npts=npts+float(s)
        xtot.append(stot/npts)
    else:
      for x in raw: xtot.append(1.)

    for n,x in enumerate(raw):
      yhi=0.
      xstep=(xhi-xlow)/1000.
      step=xlow
      for tmp in range(1000):
        xsum=0.
#        if tmp == 0.: print x
        for m in range(len(x)):
          z=(step-x[m])/(xbin/2.)
          xsum=xsum+math.exp(-0.5*z**2)
#          if tmp == 0.: print z,math.exp(-0.5*z**2),xsum
        xsum=xsum*xtot[n]
#        print xsum,yhi,
        if xsum > yhi:
#          print 'new',
          yhi=xsum
          xpeak=step
#        print
        step=step+xstep
      ymax.append(yhi)
      xmax.append(xpeak)
    if scale:
      yhi=1.1
    else:
      yhi=max(ymax)+0.1*max(ymax)
    dy=0.0015*yhi # gluge to fix plot at bottom axis
    axis([xlow,xhi,ylow+dy,yhi])
    for t,x in zip(ymax,raw):
      icolor=icolor+1
      xstep=(xhi-xlow)/1000.
      step=xlow
      v=[xlow] ; w=[0.]
      for tmp in range(1000):
        xsum=0.
        for m in range(len(x)):
          z=(step-x[m])/(xbin/2.)
          xsum=xsum+math.exp(-0.5*z**2)
        xsum=xsum*xtot[icolor]
        v.append(step)
        if scale:
          w.append(xsum/t)
        else:
          w.append(xsum)
        step=step+xstep
      plot(v,w,colors[icolor]+'-')
      a.append(xits(x,3.0)) # 3 sigma clip

  if norm == 2: icolor=-1

  if norm in [0,2]: # regular histogram
    ymax=[]
    for x in raw: 
      bin=[]
      data=[]
      for i in range(nbin+2):
        bin.append(i*xbin-xbin/2.+xlow)
        data.append(0)
      for s in x:
        for w in range(len(bin)-1):
          if s >= bin[w] and s < bin[w+1]:
            data[w]=data[w]+1
      if norm != 2:
        yhi=0.
        for w in data:
          if w > yhi: yhi=w
        ymax.append(yhi)
        a.append(xits(x,3.0)) # 3 sigma clip

      if scale:
        data=numpy.array(data)
        data=data/float(yhi)
      v=[] ; w=[] ; lastw=0.
      for xx,yy in zip(bin,data):
        v.append(xx)
        w.append(lastw)
        v.append(xx)
        w.append(yy)
        lastw=yy
      icolor=icolor+1
      plot(v,w,colors[icolor]+'-')
#      hist(x, nbin+1., range=(xlow-xbin/2.,xhi+xbin/2.), align='mid', histtype='step', edgecolor=colors[icolor])
    if scale:
      yhi=1.1
    else:
      if norm == 2:
        yhi=yhi+0.1*yhi
      else:
        yhi=max(ymax)+0.1*max(ymax)

  try:
    if '-no_peak' in sys.argv: raise
    for i,t in enumerate(xmax):
#      text(t-(xhi-xlow)/97.,yhi-0.05*(yhi-ylow),'$\uparrow$',color=colors[i])
      scatter([t],[yhi-0.05*(yhi-ylow)],s=250,marker=(4,0,0),edgecolor=colors[i],facecolor='w')
  except:
    pass

  try:
    if '-no_mean' in sys.argv: raise
    for i,t in enumerate(a):
      text(t[2]-(xhi-xlow)/97.,yhi-0.07*(yhi-ylow),'$\downarrow$',color=colors[i])
  except:
    pass

  if usetex:
    for nn,name in enumerate(filnames):
        figtext(0.91,0.90-nn*0.018,name,horizontalalignment='left',verticalalignment='top', \
                color=colors[nn],size=10)

  dy=0.0015*yhi # gluge to fix plot at bottom axis
  axis([xlow,xhi,ylow+dy,yhi]) #gludge to get bottom axis right
  tick=ticks(ax.xaxis.get_majorticklocs()[0],ax.xaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  ax.xaxis.set_minor_locator(minorLocator)
  tick=ticks(ax.yaxis.get_majorticklocs()[0],ax.yaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  ax.yaxis.set_minor_locator(minorLocator)
  xlabel(labels['x'])
  ylabel(labels['y'])
  suptitle(labels['t'])
  draw()

def get_string(event): # event routine to get strings
  global xlow,xhi,ylow,yhi,xbin,line,colors,ft,cid1,cid2,raw,labels,cmd,norm,ax,scale
#  print 'cid2 key',event.key,'cmd',cmd,'line',line

  if event.key == 'enter': # <cr> disconnect, reconnect main clicker, do action
    action()
    return 0

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
  ft=figtext(0.1,0.05,line,horizontalalignment='left',verticalalignment='top') # type the line at
                                                                               # the bottom of screen
  draw()
  return 1

def action(): # do the actions from clicker as given by var cmd
  global xlow,xhi,ylow,yhi,xbin,line,colors,ft,cid1,cid2,raw,labels,cmd,norm,ax,scale

  if cmd in ['x','t']: # add labels
    labels[cmd]=line.split(': ')[-1]

  elif cmd == 'm': # output a mongo file
    out=open(line.split(': ')[-1],'w')
    icolor=0
    if norm:
      for x in raw:
        icolor=icolor+1
        xstep=(xhi-xlow)/100
        step=xlow
        out.write(str(xlow)+' '+str(0.)+' '+str(icolor)+'\n')
        for tmp in range(100):
          xsum=0.
          for m in range(len(x)):
            z=(step-x[m])/(xbin/2.)
            xsum=xsum+math.exp(-0.5*z**2)
          out.write(str(step)+' '+str(xsum)+' '+str(icolor)+'\n')
          step=step+xstep
    else:
      nbin=int((xhi-xlow)/xbin) # initialize bins,yhi,colors
      for x in raw:
        icolor=icolor+1
        bin=[]
        data=[]
        for i in range(nbin+2):
          bin.append(i*xbin-xbin/2.+xlow)
          data.append(0)
        for s in x:
          for w in range(len(bin)-1):
            if s >= bin[w] and s < bin[w+1]:
              data[w]=data[w]+1
        for i in range(len(bin)):
          out.write(str(bin[i]+xbin/2.)+' '+str(data[i])+' '+str(icolor)+'\n')
    out.close

  elif cmd == 'f': # add another dataset
    try:
      file=open(line.split(': ')[-1],'r')
      filnames.append(line.split(': ')[-1])
      x=[]
      while 1:
        input=file.readline()
        if not input or input == '\n': break
        try:
          x.append(float(input.split()[col]))
        except:
          pass
      file.close()
      raw.append(x)
    except:
      fig.texts.remove(ft)
      ft=figtext(0.1,0.05,'FILE ERROR',horizontalalignment='left',verticalalignment='top',color='r')
      clf()
      ax = fig.add_subplot(111)
      draw_h(True)
      line=''
      return

  fig.texts.remove(ft)
  clf()
  draw_h(True)
  line=''
  return

def clicker(event): # main event handler
  global xlow,xhi,ylow,yhi,xbin,line,colors,ft,cid1,cid2,raw,labels,cmd,norm,ax,scale,trap
#  print 'cid1 key',event.key,'cmd',cmd,'line',line

  if event.key in ['x','t','f','m'] or trap: # note disconnect here and hand off to get_string
    if not trap:
      if event.key == 'x':
        line='Enter x label name: '
        cmd='x'
      if event.key == 't':
        line='Enter title: '
        cmd='t'
      if event.key == 'f':
        line='Enter file name: '
        cmd='f'
      if event.key == 'm':
        line='Enter mongo file name: '
        cmd='m'
      trap=1

    else:

      if event.key == 'enter': # <cr> disconnect, reconnect main clicker, do action
        action()
        trap=0

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
    ft=figtext(0.1,0.05,line,horizontalalignment='left',verticalalignment='top') # type the line at
    draw()

  else:

    cmd=event.key

    if event.key == '/':
      disconnect(cid1)
      close('all')
      sys.exit()

    elif event.key == 'enter': # change axes and bin
      try:
        xlow=float(line.split()[0])
        xhi=float(line.split()[1])
        xbin=float(line.split()[2])
        clf()
        ax = fig.add_subplot(111)
        draw_h(True)
        line=''
      except: # complex handler for bad inputs, flashs red message
        fig.texts.remove(ft)
        ft=figtext(0.1,0.05,'INPUT ERROR',horizontalalignment='left',verticalalignment='top',color='r')
        ax = fig.add_subplot(111)
        draw_h(True)
        line=''

    elif event.key == 's': # scale the histograms
      scale=abs(scale-1)
      clf()
      ax = fig.add_subplot(111)
      draw_h(True)

    elif event.key == 'n': # normalized histogram
#    norm=abs(norm-1)
      norm=norm+1
      if norm == 3: norm=0
      clf()
      ax = fig.add_subplot(111)
      draw_h(True)

    elif event.key == 'h': # postscript hardcopy
      draw_h(False)
      savefig('hist.pdf',orientation='landscape')
      draw_h(True)

    elif event.key == 'backspace':
      try:
        if line[-2:] != ': ': line=line[:-1]
      except:
        pass

    elif event.key in [None,'shift','control','alt','right','left','up','down','escape']:
      pass

    else:
      line=line+event.key

  try:
    fig.texts.remove(ft)
  except:
    pass
  ft=figtext(0.1,0.05,line,horizontalalignment='left',verticalalignment='top')

  draw()

if sys.argv[1] == '-h':
  print 'Usage: hist data_file column_number'
  print
  print 'options: -no_mean = supress mean markers'
  print '         -no_peak = supress peak markers'
  print
  print 'commands: lower, upper, bin size'
  print '          f = new file'
  print '          n = normalized histogram'
  print '          s = scale histograms'
  print '          h = hardcopy (hist.ps)'
  print '          m = output histogram to mongo file'
  print '          t = enter title'
  print '          x = enter xlab'
  print '          q = exit'
  sys.exit()

try:
  col=int(sys.argv[-1])
  file=open(sys.argv[-2],'r')
  filnames=[sys.argv[-2]]
except:
  col=0
  file=open(sys.argv[-1],'r')
  filnames=[sys.argv[-1]]

x=[]
raw=[]
xlow=1.e33
xhi=-1.e33
while 1:
  input=file.readline()
  if not input or input == '\n': break
  try:
    if float(input.split()[col]) != float(input.split()[col]): raise
    x.append(float(input.split()[col]))
    if float(input.split()[col]) < xlow: xlow=float(input.split()[col])
    if float(input.split()[col]) > xhi: xhi=float(input.split()[col])
  except:
    pass
file.close()
raw.append(x)

nbin=25 # initialize parameters
xbin=(xhi-xlow)/nbin
ylow=0.
labels={'x':'','y':'N','t':''}
line=''
cmd=''
norm=0
scale=0
colors=['k','r','g','b','c','m','y']
trap=0

fig = figure(figsize=(12, 8), dpi=80)  # initialize plot parameters
ax = fig.add_subplot(111)  # assign ax for text and axes
manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
manager.window.title('')
if 'deepcore' in os.uname()[1]:
  manager.window.geometry('+600+200') # move the window for deepcore big screen
else:
  manager.window.geometry('+200+50')
draw_h(True) # 1st draw

cid1=connect('key_press_event',clicker)
show() # all matplotlib scripts end with this
