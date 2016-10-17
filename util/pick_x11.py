#!/usr/bin/env python

import sys
import numarray
from ppgplot import *
from math import *

# continue useing numarray 1.5 till numpy works
# with ppgplot
#try:
#  import numpy.numarray as numarray
#except:
#  import numarray

def lzprob(z):
    Z_MAX = 6.0    # maximum meaningful z-value
    if z == 0.0:
        x = 0.0
    else:
        y = 0.5 * fabs(z)
        if y >= (Z_MAX*0.5):
            x = 1.0
        elif (y < 1.0):
            w = y*y
            x = ((((((((0.000124818987 * w
                        -0.001075204047) * w +0.005198775019) * w
                      -0.019198292004) * w +0.059054035642) * w
                    -0.151968751364) * w +0.319152932694) * w
                  -0.531923007300) * w +0.797884560593) * y * 2.0
        else:
            y = y - 2.0
            x = (((((((((((((-0.000045255659 * y
                             +0.000152529290) * y -0.000019538132) * y
                           -0.000676904986) * y +0.001390604284) * y
                         -0.000794620820) * y -0.002034254874) * y
                       +0.006549791214) * y -0.010557625006) * y
                     +0.011630447319) * y -0.009279453341) * y
                   +0.005353579108) * y -0.002141268741) * y
                 +0.000535310849) * y +0.999936657524
    if z > 0.0:
        prob = ((x+1.0)*0.5)
    else:
        prob = ((1.0-x)*0.5)
    return prob

def slice(x,y):
  if x > y: return 0.
  if x < 0 and y >= 0:
    return (lzprob(y)-0.5)+(lzprob(abs(x))-0.5)
  else:
    return abs((lzprob(abs(y))-0.5)-(lzprob(abs(x))-0.5))

def min_max(x,y):
  return min(x)-0.10*(max(x)-min(x)),max(x)+0.10*(max(x)-min(x)), \
         min(y)-0.10*(max(y)-min(y)),max(y)+0.10*(max(y)-min(y))

def perp(m,b,x,y):
# find perpenticular distance from line to x,y
  if m != 0.:
    c=y+x/m
    r=(c-b)/(m+1./m)
  else:
    r=x
  s=m*r+b
  d=((r-x)**2+(s-y)**2)**0.5
  if r <= x:
    return d
  else:
    return -d

def linfit(fit):
# linear fit to array fit (x,y,sigmay)
  sum=0.0
  sumx=0.0
  sumy=0.0
  sumxy=0.0
  sumx2=0.0
  sumy2=0.0
  n=0
  for tmp in fit:
    n+=1
    sum=sum+(1./tmp[2]**2)
    sumx=sumx+(1./tmp[2]**2)*tmp[0]
    sumy=sumy+(1./tmp[2]**2)*tmp[1]
    sumxy=sumxy+(1./tmp[2]**2)*tmp[0]*tmp[1]
    sumx2=sumx2+(1./tmp[2]**2)*tmp[0]*tmp[0]
    sumy2=sumy2+(1./tmp[2]**2)*tmp[1]*tmp[1]
  dex=sum*sumx2-sumx*sumx
# y intersect -- a
  a=(sumx2*sumy-sumx*sumxy)/dex
# slope -- b
  b=(sum*sumxy-sumx*sumy)/dex
# varience
  var=(sumy2+a*a*sum+b*b*sumx2-2.*(a*sumy+b*sumxy-a*b*sumx))/(n-2)
  if var < 0.: var=0.
# correlation coefficient -- r
  r=(sum*sumxy-sumx*sumy)/((dex*(sum*sumy2-sumy*sumy))**0.5)
# sigma b
  sigb=(var*sumx2/dex)**0.5
# sigma m
  sigm=(var*sum/dex)**0.5
  sigx=0.
  for tmp in fit:
    z=a+b*tmp[0]
    sigx=sigx+(z-tmp[1])**2
  sigx=(sigx/(n-1))**.5
  return a,b,r,sigb,sigm,sigx

def plot():
# primary plotting function
  pgeras()

# if greyscale set, the first data set was turned into an
# array, pix, for greyscale or contour plotting
  if abs(igray):
    i1=0 ; i2=pix.getshape()[0]
    j1=0 ; j2=pix.getshape()[1]
    pgswin(i1,i2,j1,j2)
    if igray == -1: # if igray = -1, contour
      pgcons_s(pix[j1:j2,i1:i2],len(c),c,i1,j1,i2,j2)
      pgsci(4)
      for n,z in enumerate(c): # label coutour marks on right side
        t=j2-(n+0.5)*(j2-j1)/len(c)
        pgptxt(i2+0.05*(i2-i1),t,0.,0.5,'%.1f' % z)
      pgsci(1)
    else: # else greyscale
      pggray_s(pix[j1:j2,i1:i2],r1,r2,i1,j1,i2,j2)
#      pgsci(4) # label greyscale limits
#      t=j2-(0+0.5)*(j2-j1)/10.
#      pgptxt(i2+0.05*(i2-i1),t,0.,0.5,'%.1f' % r2)
#      t=j2-(1+0.5)*(j2-j1)/10.
#      pgptxt(i2+0.05*(i2-i1),t,0.,0.5,'%.1f' % r1)
      pgsci(1)

# box and label axes
  pgswin(xmin,xmax,ymin,ymax)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  pglab(title[0],title[1],title[2])
  pgsch(scale) # scale can be changed

# plot floating labels
  for z in f_label:
    pgsci(z[-1])
    pgptxt(z[0],z[1],0.,0.5,z[2])
    pgsci(1)

# set colors and outlyers count
  o1 = o2 = o3 = o4 = 0

# load the points, each set a different color
# from the master array
  for i,data in enumerate(master[abs(igray):]):
    x1=[] ; x2=[] ; y1=[] ; y2=[]
    for tmp in data:
      if tmp[4] == 0: # 1st array
        x1.append(tmp[0])
        y1.append(tmp[1])
      else: # deletions 2nd array
        x2.append(tmp[0])
        y2.append(tmp[1])
      if tmp[0] > xmax: o1+=1
      if tmp[0] < xmin: o2+=1
      if tmp[1] > ymax: o3+=1
      if tmp[1] < ymin: o4+=1
    pgsci(ptype[i+abs(igray)][1])

# if dataset ptype = line, plot line, else points
    if ptype[i+abs(igray)][2] in ['line','dash']:
      pgslw(6)
      pgmove(x1[0],y1[0])
      if ptype[i+abs(igray)][2] == 'dash': pgsls(2)
      for xs,ys in zip(x1,y1): pgdraw(xs,ys)
      pgsls(1)
      pgslw(1)
    else:
      if not label:
        xs=numarray.array(x1) ; ys=numarray.array(y1)
        pgpt(xs,ys,ptype[i+abs(igray)][0]) # ptype for data
        xs=numarray.array(x2) ; ys=numarray.array(y2)
        pgpt(xs,ys,5) # x's for deletions
      else: # or use labels instead of points
        if slabel:
          imin=1.e33
          imax=-1.e33
          for tmp in data:
            if float(tmp[-1]) < imin: imin=float(tmp[-1])
            if float(tmp[-1]) > imax: imax=float(tmp[-1])
          mz=(0.5-4.)/(imin-imax)
          tz=-mz*imin+0.5
          for tmp in data: 
            if tmp[4] == 0 and tmp[0] > xmin and tmp[0] < xmax and tmp[1] > ymin and tmp[1] < ymax:
              xs=numarray.array([tmp[0]]) ; ys=numarray.array([tmp[1]])
              pgsch(mz*float(tmp[-1])+tz)
              pgpt(xs,ys,ptype[i+abs(igray)][0])
        else:
          for tmp in data: 
            if tmp[4] == 0 and tmp[0] > xmin and tmp[0] < xmax and tmp[1] > ymin and tmp[1] < ymax:
              pgptxt(tmp[0],tmp[1],0.,0.5,tmp[5])
  pgsch(1.)
  pgsci(1)

# plot linear fits if they exist
  try:
    a # a & b = regular fit, ax & bx = biweight fit
    pgsch(0.7)
    pgmove(xmin,b*xmin+a)
    pgdraw(xmax,b*xmax+a)
    step=0.035*(ymax-ymin)
    yp=ymax-step/2.
    xp=xmin
    strng='m = '+'%5.4g' % b+' +/- '+'%5.4g' %sigm
    pgptxt(xp,yp+3.*step,0.,0.0,strng)
    strng='b = '+'%5.4g' % a+' +/- '+'%5.4g' %sigb
    pgptxt(xp,yp+2.*step,0.,0.0,strng)
    strng='R = '+'%5.4g' % r
    pgptxt(xp,yp+step,0.,0.0,strng)
    pgsci(2)
    pgmove(xmin,bx*xmin+ax)
    pgdraw(xmax,bx*xmax+ax)
    xp=xmin+0.38*(xmax-xmin)
    strng='m = '+'%5.4g' % bx+' +/- '+'%5.4g' %sigmx
    pgptxt(xp,yp+3.*step,0.,0.0,strng)
    strng='b = '+'%5.4g' % ax+' +/- '+'%5.4g' %sigbx
    pgptxt(xp,yp+2.*step,0.,0.0,strng)
    strng='R = '+'%5.4g' % rx
    pgptxt(xp,yp+step,0.,0.0,strng)
    pgsci(3)
    pgmove(xmin,bz*xmin+az)
    pgdraw(xmax,bz*xmax+az)
    xp=xmin+0.75*(xmax-xmin)
    strng='m = '+'%5.4g' % bz
    pgptxt(xp,yp+3.*step,0.,0.0,strng)
    strng='b = '+'%5.4g' % az
    pgptxt(xp,yp+2.*step,0.,0.0,strng)
    pgsch(1.)
    pgsci(1)
    if delsig != 3.1: # if deletion sigma changed from default
      strng='deletion sigma = '+'%4.2g' % delsig
      pgptxt(xmin,ymin-3.5*step,0.,0.0,strng)
  except:
    if (o1+o2+o3+o4): # show number of outlyers in upper left
#      pgsci(2)
#      pgptxt(xmin+0.08*(xmax-xmin),ymax+0.06*(ymax-ymin),0.,0.5,str(o1))
#      pgptxt(xmin,ymax+0.06*(ymax-ymin),0.,0.5,str(o2))
#      pgptxt(xmin+0.04*(xmax-xmin),ymax+0.10*(ymax-ymin),0.,0.5,str(o3))
#      pgptxt(xmin+0.04*(xmax-xmin),ymax+0.02*(ymax-ymin),0.,0.5,str(o4))
      pgsch(1.)
      pgsci(1)

# draw manual lines
  for z in lines:
    pgsci(z[2])
    pgmove(xmin,z[0]*xmin+z[1])
    pgdraw(xmax,z[0]*xmax+z[1])
    pgsci(1)

def read_win(line):
  tmp=''
  pgsci(1)
  pgswin(0.,1.,0.,1.)
  pgptxt(0.,-.1,0.,0.,line)
  while 1:
    d=pgband(0)
    if d[2] == '\r':
      return tmp
    else:
      if d[2] == '\b':
        pgsci(0)
        pgptxt(0.,-.1,0.,0.,line+tmp)
        tmp=tmp[:-1]
        pgsci(1)
        pgptxt(0.,-.1,0.,0.,line+tmp)
      else:
        tmp=tmp+d[2]
      pgptxt(0.,-.1,0.,0.,line+tmp)

def help():
  print
  print '/ = exit               b = change borders'
  print 'r = reset              y = enter axes labels'
  print 'h = hardcopy           m = draw a line segment'
  print
  print 't = toggle labels      s = scale size of labels'
  print 'e = plot error bars    p = change current plot style'
  print 'u = use label as size for points'
  print
  print 'f = use new file, increment color and style'
  print '    files ending in .line, connected'
  print '    files ending in .dash, dashed'
  print
  print 'g = grayscale          c = contrast control'
  print 'n = normalized gray    z = contour plot'
  print
  print 'l = linear fit (rotates through datasets)'
  print 'x,1,2,3,4 = delete points (individual, quads)'
  print 'd = delete sigma from fit, each hit lowers sigma'
  print
  print 'o = output points into ok (pick.ok)'
  print '    and deletion files (pick.dels)'
  print

# main

if len(sys.argv) <= 1 or sys.argv[1] == '-h':
  print 'Usage: pick op filename xcol ycol'
  print
  print '>>> not-so-quick plotting script <<<'
  print
  print 'file needs x,y points in any column, but labels'
  print 'need to be in the last column.  If filename has'
  print '"*" in it, reads all those files'
  print
  print 'Options: -win = set PGPLOT window size'
  print '                default is 10 inches'
  print '           -b = start borders (x1,x2,y1,y2)'
  print '        -exit = plot then exit'
  help()
  sys.exit()

# initialize PGPLOT window, note 10 inch window to start
pgbeg('/xs',1,1)
pgask(0)
pgscr(0,1.,1.,1.)
pgscr(1,0.,0.,0.)
pgscf(2)

if '-win' in sys.argv:
  pgpap(float(sys.argv[sys.argv.index('-win')+1]),1.0)
else:
  pgpap(10.0,1.0)

# look for column numbers in sys.argv
try:
  i=int(sys.argv[-2])
  j=int(sys.argv[-1])
except:
  i=0
  j=1

master=[] ; ptype=[] ; x=[] ; y=[] ; data=[]   # initialize master list
icol=0                                         # color type

# look for filename in sys.argv
sys.argv.reverse()
for filename in sys.argv:
  try:
    int(filename)
  except:
    break
sys.argv.reverse()

pgplot_colors=['white','black','red','green','blue','cyan','purple','yellow','orange','lt green','slate']

try:
  int(sys.argv[-2])
  tail=-2
except:
  tail=None
front=1
if '-exit' in sys.argv: front+=1
if '-win' in sys.argv: front+=1
if '-b' in sys.argv: front=front+5

for file in sys.argv[front:tail]:
  icol+=1
  print 'loading ...',file,pgplot_colors[icol]
  try:
    input=open(file,'r')
  except:
    print 'file name',file,'not found'
    sys.exit()
  data=[]
  while 1:
    line=input.readline()
    if not line or len(line) < 2: break
    x.append(float(line.split()[i]))
    y.append(float(line.split()[j]))
    try:
      data.append([float(line.split()[i]),float(line.split()[j]),float(line.split()[i+2]),
                   float(line.split()[i+3]),0,line.split()[-1]])
    except:
      data.append([float(line.split()[i]),float(line.split()[j]),0.,0.,0,line.split()[-1]])
  master.append(data)
  if '.line' in file: # look at file name to determine ptype
    ptype.append([3,icol,'line'])
  elif '.dash' in file:
    ptype.append([3,icol,'dash'])
  else:
    ptype.append([3,icol,'points'])
  input.close()

# data read in as 
# 0,1: x and y in input i and j columns
# 2,3: errorbars for x and y, assumed to be in column i+2 and i+3 of raw data
# 4: kill for linear fitting
# 5: label assumed to be in last column of data file
# label found, not errorbars

# initialize parameters
label=0                           # label flag
slabel=0                          # size label flag
scale=1.                          # scale for labels
delsig=3.1                        # deletion sigma for linfit
ifit=0                            # which set used for linfit
title=['','','']                  # plot titles
errorbar=0                        # errorbar flag
igray=0                           # greyscale flag
iborder=1                         # manual borders flag
box=5.                            # size of greyscale/contour bin
f_label=[]                        # floating labels
lines=[]                          # line marks

xmin,xmax,ymin,ymax=min_max(x,y)  # set boundaries
if '-b' in sys.argv:
  xmin=float(sys.argv[sys.argv.index('-b')+1])
  xmax=float(sys.argv[sys.argv.index('-b')+2])
  ymin=float(sys.argv[sys.argv.index('-b')+3])
  ymax=float(sys.argv[sys.argv.index('-b')+4])

plot() # main plot function

if '-exit' in sys.argv: sys.exit()

while 1:

  d=pgband(0) # read the cursor

  if d[2] == '?': # help
    help()

  if d[2] == '.': # info on nearest point
    rmin=1.e33
    for n,z in enumerate(master[ifit]):
      if ((z[0]-d[0])**2+(z[1]-d[1])**2)**0.5 < rmin:
        imin=n
        rmin=((z[0]-d[0])**2+(z[1]-d[1])**2)**0.5
    if label:
      print master[ifit][imin][0],master[ifit][imin][1],master[ifit][imin][-1]
    else:
      print master[ifit][imin][0],master[ifit][imin][1]

  if d[2] == 'h': # do a hardcopy, convert to pdf
    pgend()
    pgbeg('tmp.ps/vcps',1,1)
    pgask(0)
    pgscr(0,1.,1.,1.)
    pgscr(1,0.,0.,0.)
    pgscf(2)
    pgpap(8.0,1.0)
    import os
    plot()
    pgend()
    os.system('ps2pdf tmp.ps')
    print 'output to tmp.ps & tmp.pdf'
    pgbeg('/xs',1,1)
    pgask(0)
    pgscr(0,1.,1.,1.)
    pgscr(1,0.,0.,0.)
    pgscf(2)
    pgpap(10.0,1.0)
    plot()

  if d[2] == 'p': # change plot style
    tmp=read_win('Enter point style ['+str(ptype[-1][0])+']: ')
    if len(tmp): ptype[-1][0]=int(tmp)
    plot()
    tmp=read_win('Enter color style ['+str(ptype[-1][1])+']: ')
    if len(tmp): ptype[-1][1]=int(tmp)
    plot()
    tmp=read_win('Enter line style ['+str(ptype[-1][2])+']: ')
    if len(tmp): ptype[-1][2]=tmp
    plot()

  if d[2] == 'c': # change contrast with cursor
    k=0.5+(d[0]-xmin)/(xmax-xmin)
    try:
      r1=r1*k
    except:
      r1=0.
    r2=0.          # set contour levels and/or contrast
    c=numarray.array(numarray.arange(r2,r1,(r1-r2)/10.))
    plot()

  if d[2] in ['g','n','z']: # build an array
    box=int(box*2.) # box size for binning, reduce each time
    igray=1    # set switch
    dx=(xmax-xmin)/box
    dy=(ymax-ymin)/box
    pix=numarray.zeros((box,box),'Float32')
    r1=0. ; r2=0.
    for jj,y in enumerate(numarray.arange(ymin+dy/2.,ymax+dy/2.,dy)):
      for ii,x in enumerate(numarray.arange(xmin+dx/2.,xmax+dx/2.,dx)):
        if x >= xmax-dx/4. or y >= ymax-dy/4.: continue # gluge here cause arange
        n=0.                                            # sometimes uses last element
        if d[2] == 'g': # regular binning
          for t in master[ifit]:
            if t[0] >= x and t[0] < x+dx and t[1] >= y and t[1] < y+dy: n+=1
        else:           # normalized binning, sigma=dx/2
          for t in master[ifit]:
            if t[4] == 0:
              n1=slice(-(t[0]-(x-dx/2.))/dx,-(t[0]-(x+dx/2.))/dx)
              n2=slice(-(t[1]-(y-dy/2.))/dy,-(t[1]-(y+dy/2.))/dy)
# enter your own errors disabled
#            else:
#              n1=slice(-(t[0]-(x-dx/2.))/t[2],-(t[0]-(x+dx/2.))/t[2])
#              n2=slice(-(t[1]-(y-dy/2.))/t[3],-(t[1]-(y+dy/2.))/t[3])
            n=n+n1*n2
        pix[jj][ii]=n # load up array
        if n > r1: r1=n+2
    if d[2] == 'z': # for a contour
      igray=-1
      c=numarray.array(numarray.arange(r2,r1,(r1-r2)/10.))
    plot()

  if d[2] == 'w': # write floating labels
    tmp=read_win('Enter label: ')
    f_label.append([d[0],d[1],tmp,len(master)])
    while 1:
      plot()
      d=pgband(0)
      if d[2] == '\r': break
      f_label[-1]=[d[0],d[1],tmp,len(master)]
    plot()

  if d[2] == 'm': # draw a line segment (e.g. test 1-to-1)
    tmp=read_win('Enter slope, zeropt, color: ')
    lines.append([float(tmp.split()[0]),float(tmp.split()[1]),int(tmp.split()[2])])
    plot()
#    for n,line in enumerate(['Enter 1st point: ','Enter 2nd point: ']):
#      tmp=read_win(line)
#      if n == 0:
#        x1=float(tmp.split()[0])
#        y1=float(tmp.split()[1])
#        plot()
#      else:
#        plot()
#        pgsci(2)
#        pgmove(x1,y1)
#        pgdraw(float(tmp.split()[0]),float(tmp.split()[1]))
#        pgsci(1)

  if d[2] == 'y': # enter x&y labels, title
    for i,line in enumerate(['Enter xlabel: ','Enter ylabel: ','Enter title: ']):
      title[i]=read_win(line)
      plot()

  if d[2] == '/': # main exit
    break

  if d[2] == 'e': # toggle errorbars (not working)
    errorbar=1
    plot()

  if d[2] == 'f': # add a new file
    file=read_win('Enter new file name: ')
    try:
      input=open(file,'r')
      data=[]
      while 1:
        line=input.readline()
        if not line or len(line) < 2: break
        try:
          data.append([float(line.split()[i]),float(line.split()[j]),float(line.split()[i+2]),
                       float(line.split()[i+3]),0,line.split()[-1]])
        except:
          data.append([float(line.split()[i]),float(line.split()[j]),0.,0.,0,line.split()[-1]])
      master.append(data)
      icol+=1
      if '.line' in file: # look at file name to determine ptype
        ptype.append([3,icol,'line'])
      elif '.dash' in file:
        ptype.append([3,icol,'dash'])
      else:
        ptype.append([3,icol,'points'])
      input.close()
    except:
      print 'file "'+file+'" not found'
    x=[] ; y=[]
    if not abs(igray) and iborder:
      for w in master:
        for z in w:
          x.append(z[0])
          y.append(z[1])
      xmin,xmax,ymin,ymax=min_max(x,y)
    plot()

  if d[2] == 'b' or d[2] == 'B': # redo borders
    iborder=0 # stick the borders
    igray=0 # reset greyscale
    if d[2] == 'B':
      xmin=float(d[0])
      ymin=float(d[1])
      plot()
      d=pgband(0)
      xmax=float(d[0])
      ymax=float(d[1])
    else:
      tmp=read_win('Enter xmin,xmax: ')
      xmin=float(tmp.split()[0])
      xmax=float(tmp.split()[1])
      plot()
      tmp=read_win('Enter ymin,ymax: ')
      ymin=float(tmp.split()[0])
      ymax=float(tmp.split()[1])
    plot()

  if d[2] == 'r': # reset all parameters
    igray=0 ; x=[] ; y=[] ; box=5. ; iborder=1
    label=0 ; scale=1. ; ifit=0
    for w in master:
      for z in w:
        x.append(z[0])
        y.append(z[1])
    xmin,xmax,ymin,ymax=min_max(x,y)
    plot()

  if d[2] == 't': # toggle the labels on/off
    label=abs(label-1)
    plot()

  if d[2] == 'u': # toggle the labels on/off
    label=abs(label-1)
    slabel=abs(slabel-1)
    plot()

  if d[2] == 's': # scale the labels
    scale=scale*(d[0]*1.5/(xmax-xmin)+0.5-1.5*xmin/(xmax-xmin))
    plot()

  if d[2] == 'l': # fit a line
    fit=[]
    for z in master[ifit]:
      if z[4] == 0: fit.append([z[0],z[1],1.])
    a,b,r,sigb,sigm,sig=linfit(fit) # regular fit

    ax=a # biweight fit
    bx=b
    for n in range(10):
      sig=[]
      xmean=0.
      for z in master[ifit]:
        if z[4] == 0: 
          xmean=xmean+perp(bx,ax,z[0],z[1])
          sig.append(perp(bx,ax,z[0],z[1]))
      xmean=xmean/len(sig)
      sigma=0.
      for tmp in sig:
        sigma=sigma+(xmean-tmp)**2
      sigma=(sigma/(len(sig)-1.))**0.5
      fit=[]
      for z in master[ifit]:
        if z[4] == 0: 
          ss=abs(perp(bx,ax,z[0],z[1])/sigma)
          if ss < .5: ss=.5
          fit.append([z[0],z[1],ss])
      ax,bx,rx,sigbx,sigmx,sigx=linfit(fit)

    ay=ax # y-x fit, for fit of two independent variables
    by=bx
    for n in range(10):
      sig=[]
      xmean=0.
      for z in master[ifit]:
        if z[4] == 0: 
          xmean=xmean+perp(by,ay,z[1],z[0])
          sig.append(perp(by,ay,z[1],z[0]))
      xmean=xmean/len(sig)
      sigma=0.
      for tmp in sig:
        sigma=sigma+(xmean-tmp)**2
      sigma=(sigma/(len(sig)-1.))**0.5
      fit=[]
      for z in master[ifit]:
        if z[4] == 0: 
          ss=abs(perp(by,ay,z[1],z[0])/sigma)
          if ss < .5: ss=.5
          fit.append([z[1],z[0],ss])
      ay,by,ry,sigby,sigmy,sigy=linfit(fit)

# find mean slope and intercept for independent fit
    tx=(by*ax+ay)/(1.-by*bx)
    ty=bx*tx+ax
    bz=(bx+1./by)/2.
    az=ty-bz*tx

    plot()

    ifit=ifit+1 # loop through files to fit
    if ifit == len(master): ifit=0

  if d[2] == 'd': # delete points N sigma from line
    try:
      a
      delsig=delsig-delsig*0.1
      tank=[]
      if ifit == 1 or ifit == 0:
        itest=0
      else:
        itest=ifit-1
      for i,data in enumerate(master):
        if i == itest:
          for n,tmp in enumerate(data):
            ss=abs(perp(bx,ax,tmp[0],tmp[1])/sigma)
            if ss > delsig: data[n][4]=-1
        tank.append(data)
      master=tank
      plot()
    except:
      print 'no fit performed yet'

  if d[2] in ['1','2','3','4','x']: # delete points from fitting
    rmin=1.e33
    tank=[]
    if ifit == 1 or ifit == 0:
      itest=0
    else:
      itest=ifit-1
    for i,data in enumerate(master):
      if i == itest:
        for n,tmp in enumerate(data):
          r=((d[0]-tmp[0])**2+(d[1]-tmp[1])**2)**0.5
          if r <= rmin:
            rmin=r
            imin=n
          if d[2] == '1' and tmp[0] > d[0] and tmp[1] > d[1]: data[n][4]=abs(data[n][4]-1)
          if d[2] == '2' and tmp[0] < d[0] and tmp[1] > d[1]: data[n][4]=abs(data[n][4]-1)
          if d[2] == '3' and tmp[0] < d[0] and tmp[1] < d[1]: data[n][4]=abs(data[n][4]-1)
          if d[2] == '4' and tmp[0] > d[0] and tmp[1] < d[1]: data[n][4]=abs(data[n][4]-1)
        if d[2] == 'x': data[imin][4]=abs(data[imin][4]-1)
      tank.append(data)
    master=tank
    plot()

  if d[2] == 'o':
    out1=open('pick.ok','w')
    out2=open('pick.dels','w')
    print 'data output to pick.ok and pick.dels'
    for i,data in enumerate(master):
      for n,tmp in enumerate(data):
        if tmp[4]:
          print >> out2,tmp[0],tmp[1]
        else:
          print >> out1,tmp[0],tmp[1]
    out1.close()
    out2.close()
