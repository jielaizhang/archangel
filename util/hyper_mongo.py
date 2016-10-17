#!/usr/bin/env python

import sys,os,numpy,time
from math import *
from matplotlib import rc
from pylab import *
from matplotlib import pyplot
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

#main

if len(sys.argv) <= 1 or sys.argv[1] == '-h':
  print 'Usage: mongo cmd_filename'
  print
  print 'output to cmd_filename.pdf'
  print
  print 'options: -v = verbose'
  print '         -c = ignore shell commands'
  print '    -nodisp = do not display .pdf'
  print
  print 'note: ptype = N 0 solid'
  print '            = N 1 star'
  print '            = N 2 cross'
  print '            = N 3 open'
  print 'where N is number of sides'
  print 'also:'
  print '  . point  , pixel  o circle'
  print '  v triangle_down  8 octagon'
  print '  ^ triangle_up    s square'
  print '  < triangle_left  p pentagon'
  print '  > triangle_right * star'
  print '  h hexagon1       H hexagon2'
  print '  + plus           x x'
  print '  D diamond        d thin_diamond'
  print '  | vline          _ hline'
  print '  TICKLEFT         TICKRIGHT'
  print '  TICKUP           TICKDOWN'
  print '  CARETLEFT        CARETRIGHT'
  print '  CARETUP          CARETDOWN'
  sys.exit()

fig = figure(figsize=(8,8), dpi=80)
clf()

#initialize arrays
colors={'black':'k','red':'r','blue':'b','green':'g','cyan':'c','yellow':'y','magenta':'m'}
ltypes={'1':'-','2':'--','3':':'}
align={2:'left',1:'center',0:'right',6:'top',5:'center',4:'bottom'}

#initialize parameters
ptype=(6,2,0)
facec='black'
edgec='black'
angle=0.
expand=1.0
iltype='1'
icol='black'
ipy=0
font_size=12
#font = {'family' : 'normal',
#        'weight' : 'bold',
#        'size'   : 12}
#rc('font', **font)
#rc('text',usetex=True)

lines=[tmp.split() for tmp in open(sys.argv[-1],'r').readlines()]

for n,line in enumerate(lines):

  if '-v' in sys.argv: print ' '.join(line)

  if line[0] == '#!' and '-c' not in sys.argv: # run shell commands
    os.system(' '.join(line[1:]))

  if line[0][0] == '#': continue

  if line[0] == 'device':
    ipy=1

  if line[0] == 'location':
    try:
      xaxis1=float(line[1])
      xaxis2=float(line[2])
      yaxis1=float(line[3])
      yaxis2=float(line[4])
      if xaxis1 > 1.:
        xaxis1=xaxis1/32000.-0.05
        xaxis2=xaxis2/32000.-0.05
        yaxis1=yaxis1/32000.-0.1
        yaxis2=yaxis2/32000.-0.1
        ipy=1
      ax = fig.add_axes([xaxis1,yaxis1,xaxis2-xaxis1,yaxis2-yaxis1])
    except:
      print 'error in location command, line #',n
      sys.exit()

  if line[0] == 'data':
    filename=line[-1]
    if not os.path.exists(filename):
      print 'data file does not exist >>',filename,'<< line #',n
      sys.exit()

  if line[0] == 'ptype':
    try:
      if len(line) == 2:
        ptype=line[1]
      elif line[2] == '3':
        facec='none'
        ptype=(int(line[1]),0,angle)
      else:
        facec=colors[icol]
        ptype=(int(line[1]),int(line[2]),angle)
    except:
      print 'error in ptype command, line #',n
      sys.exit()

  if line[0] == 'read':
    try:
      columns={} ; var=None
      for col in line[1:]:
        if not var:
          var=col.replace('{','').replace('}','')
        else:
          columns[var]=int(col.replace('{','').replace('}',''))-ipy
          var=None

      data=[tmp.split() for tmp in open(filename,'r').readlines()]
      if len(data[-1]) == 0:
        data.pop()
      if '-v' in sys.argv: print '>>',len(data),'lines read'

    except:
      print 'error in read command, line #',n
      sys.exit()

  if line[0] == 'limits':
    try:
      if ' '.join(line) == 'limits 0 1 0 1':
        ilim=1
      else:
        ilim=0
        xmin=float(line[1]) ; xmax=float(line[2])
        ymin=float(line[3]) ; ymax=float(line[4])
        axis([xmin,xmax,ymin,ymax])
    except:
      print 'error in limits command, line #',n
      sys.exit()

  if line[0] == 'expand':
    try:
      expand=float(line[1])
    except:
      print 'error in expand command, line #',n
      sys.exit()

  if line[0] == 'angle':
    try:
      angle=float(line[1])
      ptype=(ptype[0],ptype[1],angle)
    except:
      print 'error in angle command, line #',n
      sys.exit()

  if line[0] == 'ctype':
    try:
      icol=line[1]
      facec=line[1]
      edgec=line[1]
    except:
      print 'error in ctype command, line #',n
      sys.exit()

  if line[0] == 'ltype':
    try:
      iltype=line[1]
    except:
      print 'error in ltype command, line #',n
      sys.exit()

  if line[0] == 'connect':
    try:
      x=[] ; y=[]
      for z in data:
        x.append(float(z[columns[line[1]]]))
        y.append(float(z[columns[line[2]]]))
      axis([xmin,xmax,ymin,ymax])
      ax.plot(x,y,colors[icol]+ltypes[iltype],linewidth=expand*1.0)
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymin,ymax)
    except:
      print 'error in connect command, line #',n
      sys.exit()

  if line[0] == 'hist':
    try:
      x=[] ; y=[] 
      bin=abs((float(data[0][columns[line[1]]])-float(data[1][columns[line[1]]]))/2.)
      for z in data:
        x.append(float(z[columns[line[1]]])-bin)
        y.append(float(z[columns[line[2]]]))
        x.append(float(z[columns[line[1]]])+bin)
        y.append(float(z[columns[line[2]]]))
      x.append(x[-1]) ; y.append(0.)
      x.append(x[0]) ; y.append(0.)
      x.append(x[0]) ; y.append(y[0])
      ax.plot(x,y,colors[icol]+'-',linewidth=expand*1.0)
      if line[-1] != line[2]:
        ax.fill(x,y,colors[icol])
#        ax.fill(x,y,'w',hatch='+')
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymin,ymax)
    except:
      print 'error in hist command, line #',n
      sys.exit()

  if line[0] == 'points':
    try:
      x=[] ; y=[] ; pt_size=[]
      for z in data:
        try:
          x.append(float(z[columns[line[1]]]))
          y.append(float(z[columns[line[2]]]))
          pt_size.append(float(z[columns[line[-1]]]))
        except:
          pass
      if len(line) > 3: # scale point size
        ax.scatter(x,y,s=pt_size,marker=ptype,color=colors[icol],facecolors=facec,edgecolors=edgec)
      else:
        ax.scatter(x,y,s=expand*50.,marker=ptype,color=colors[icol],facecolors=facec,edgecolors=edgec)
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymin,ymax)
    except:
      raise
      print 'error in points command, line #',n
      sys.exit()

  if line[0] == 'labels':
    try:
      x=[] ; y=[] ; labels=[]
      for z in data:
        x.append(float(z[columns[line[1]]]))
        y.append(float(z[columns[line[2]]]))
        labels.append(z[columns[line[3]]])
      for xc,yc,label in zip(x,y,labels):
        ax.text(xc,yc,label, fontsize=int(expand*font_size), \
              color=colors[icol], rotation=angle, \
              horizontalalignment='center', verticalalignment='center')
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymin,ymax)
    except:
      print 'error in labels command, line #',n
      sys.exit()

  if line[0] == 'errorbars':
    try:
      x=[] ; y=[] ; ex_up=[] ; ex_dn=[] ; ey_up=[] ; ey_dn=[]
      for z in data:
        x.append(float(z[columns[line[1]]]))
        y.append(float(z[columns[line[2]]]))
        if line[4] != 'null':
          ex_up.append(float(z[columns[line[4]]]))
        if line[3] != 'null':
          ex_dn.append(float(z[columns[line[3]]]))
        if line[6] != 'null':
          ey_up.append(float(z[columns[line[6]]]))
        if line[5] != 'null':
          ey_dn.append(float(z[columns[line[5]]]))
      if line[4] != 'null':
        ax.errorbar(x,y,xerr=[ex_up,ex_dn],color=colors[icol],ls='none')
      if line[6] != 'null':
        ax.errorbar(x,y,yerr=[ey_up,ey_dn],color=colors[icol],ls='none')
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymin,ymax)
    except:
      print 'error in errorbars command, line #',n
      sys.exit()

  if line[0] == 'box':
# note: default is box 1 2
# 0 = no labels
# 1 = labels parallel
# 2 = labels pertpentical
# 3 = no labels, no ticks

    try:
      if len(line) == 1:
        tick=ticks(ax.xaxis.get_majorticklocs()[0],ax.xaxis.get_majorticklocs()[1])
        minorLocator=MultipleLocator(tick)
        ax.xaxis.set_minor_locator(minorLocator)
        tick=ticks(ax.yaxis.get_majorticklocs()[0],ax.yaxis.get_majorticklocs()[1])
        minorLocator=MultipleLocator(tick)
        ax.yaxis.set_minor_locator(minorLocator)
        for tick in ax.xaxis.get_major_ticks():
          tick.label.set_fontsize(int(expand*font_size)) 
        for tick in ax.yaxis.get_major_ticks():
          tick.label.set_fontsize(int(expand*font_size)) 
        ax.xaxis.set_tick_params(size=int(expand*5), which='minor')
        ax.xaxis.set_tick_params(size=int(expand*10), which='major')
        ax.yaxis.set_tick_params(size=int(expand*5), which='minor')
        ax.yaxis.set_tick_params(size=int(expand*10), which='major')
        for side in ['top','bottom','left','right']:
          ax.spines[side].set_linewidth(expand*1.0)

      else:
        if line[1] in ['0','1']:
          tick=ticks(ax.xaxis.get_majorticklocs()[0],ax.xaxis.get_majorticklocs()[1])
          minorLocator=MultipleLocator(tick)
          ax.xaxis.set_minor_locator(minorLocator)
          tick=ticks(ax.yaxis.get_majorticklocs()[0],ax.yaxis.get_majorticklocs()[1])
          minorLocator=MultipleLocator(tick)
          ax.yaxis.set_minor_locator(minorLocator)
          if line[1] == '1':
            for tick in ax.xaxis.get_major_ticks():
              tick.label.set_fontsize(int(expand*font_size)) 
              if line[2] == '1':
                tick.label.set_rotation('vertical')
              else:
                tick.label.set_rotation('horizontal')
          else:
            ax.tick_params(axis='x',labelbottom='off')
          ax.xaxis.set_tick_params(size=int(expand*5), which='minor')
          ax.xaxis.set_tick_params(size=int(expand*10), which='major')
          ax.yaxis.set_tick_params(size=int(expand*5), which='minor')
          ax.yaxis.set_tick_params(size=int(expand*10), which='major')
          for side in ['top','bottom','left','right']:
            ax.spines[side].set_linewidth(expand*1.0)
        if line[1] == '3':
          ax.tick_params(axis='x',          # changes apply to the x-axis
                         which='both',      # both major and minor ticks are affected
                         bottom='off',      # ticks along the bottom edge are off
                         top='off',         # ticks along the top edge are off
                         labelbottom='off') # labels along the bottom edge are off

        if line[2] in ['0','1','2']:
          tick=ticks(ax.xaxis.get_majorticklocs()[0],ax.xaxis.get_majorticklocs()[1])
          minorLocator=MultipleLocator(tick)
          ax.xaxis.set_minor_locator(minorLocator)
          tick=ticks(ax.yaxis.get_majorticklocs()[0],ax.yaxis.get_majorticklocs()[1])
          minorLocator=MultipleLocator(tick)
          ax.yaxis.set_minor_locator(minorLocator)
          if line[2] in ['1','2']:
            for tick in ax.yaxis.get_major_ticks():
              tick.label.set_fontsize(int(expand*font_size)) 
              if line[2] == '1':
                tick.label.set_rotation('vertical')
              else:
                tick.label.set_rotation('horizontal')
          else:
            ax.tick_params(axis='y',labelleft='off')
          ax.xaxis.set_tick_params(size=int(expand*5), which='minor')
          ax.xaxis.set_tick_params(size=int(expand*10), which='major')
          ax.yaxis.set_tick_params(size=int(expand*5), which='minor')
          ax.yaxis.set_tick_params(size=int(expand*10), which='major')
          for side in ['top','bottom','left','right']:
            ax.spines[side].set_linewidth(expand*1.0)
        if line[2] == '3':
          ax.tick_params(axis='y',          # changes apply to the x-axis
                         which='both',      # both major and minor ticks are affected
                         left='off',      # ticks along the bottom edge are off
                         right='off',         # ticks along the top edge are off
                         labelleft='off') # labels along the bottom edge are off

    except:
      print 'error in box command, line #',n
      sys.exit()

  if line[0] == 'xlabel':
    try:
      xlabel(' '.join(line[1:]),fontsize=int(expand*font_size))
    except:
      print 'error in xlabel command, line #',n
      sys.exit()
#    ax.text((xmax-xmin)/2.+xmin,ymin-0.04*(ymax-ymin)/(yaxis2-yaxis1), ' '.join(line[1:]), fontsize=int(expand*font_size), \
#            horizontalalignment='center',verticalalignment='center')

  if line[0] == 'ylabel':
    try:
      ylabel(' '.join(line[1:]),fontsize=int(expand*font_size))
    except:
      print 'error in ylabel command, line #',n
      sys.exit()

  if line[0] == 'title':
    try:
      suptitle(' '.join(line[1:]),fontsize=int(expand*font_size))
    except:
      print 'error in title command, line #',n
      sys.exit()

  if line[0] == 'relocate':
    try:
      xc=float(line[1])
      yc=float(line[2])
    except:
      print 'error in relocate command, line #',n
      sys.exit()

  if line[0] == 'draw':
    try:
      ax.plot([xc,float(line[1])],[yc,float(line[2])],colors[icol]+ltypes[iltype],linewidth=expand*1.0)
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymin,ymax)
    except:
      print 'error in draw command, line #',n
      sys.exit()

  if line[0] in ['putl','putx']:
#               label to left     centre     right
#        label above      7         8         9 
#              centered   4         5         6
#              below      1         2         3
#align={2:'left',1:'center',0:'right',6:'top',5:'center',4:'bottom'}

    try:
      if line[0] == 'putx' or ilim:
        ax.text(xc*(xmax-xmin)+xmin,yc*(ymax-ymin)+ymin,' '.join(line[2:]), \
                fontsize=int(expand*font_size), \
                color=colors[icol], rotation=angle, \
                horizontalalignment=align[((int(line[1])-1) % 3)], \
                verticalalignment=align[int((int(line[1])-1)/3)+4])
      else:
        ax.text(xc,yc,' '.join(line[2:]), fontsize=int(expand*font_size), \
                color=colors[icol], rotation=angle, \
                horizontalalignment=align[((int(line[1])-1) % 3)], \
                verticalalignment=align[int((int(line[1])-1)/3)+4])
    except:
      print 'error in putl command, line #',n
      sys.exit()

  if line[0] == 'end':
    fig.savefig(sys.argv[-1].split('.')[0]+'.pdf',dpi=100)
    if '-nodisp' not in sys.argv:
      tmp=os.popen('ps -acjx | grep TeXShop').read()
      if 'TeXShop' in tmp:
        os.system('kill -9 '+tmp.split()[1])
      time.sleep(0.5)
      os.system('/Applications/TeX/TeXShop.app/Contents/MacOS/TeXShop '+sys.argv[-1].split('.')[0]+'.pdf &')


    sys.exit()
