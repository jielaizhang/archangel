#!/usr/bin/env python

import sys,os,time,subprocess
from math import *
from matplotlib import rc
from pylab import *
from matplotlib.ticker import MultipleLocator # needed to fix up minor ticks
import warnings ; warnings.simplefilter('ignore')

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

def draw_x(usetex):
  global switch,axe,xmin,xmax,ymin,ymax,line,cmd,cid1,cid2,ft,master,ifile,box,pix,igray,r1,r2,ifit,label,dx,dy,f_label,filenames,ptype,lines
# primary plotting function

  if '-tex' in sys.argv: usetex=True
  ioff()
  clf() ; axe = fig.add_subplot(111)
  rc('text',usetex=usetex)

# if greyscale set, the first data set was turned into an
# array, pix, for greyscale or contour plotting
  if abs(igray):
    i1=0 ; i2=pix.shape[0]
    j1=0 ; j2=pix.shape[1]
    if igray == -1: # if igray = -1, contour
      contour(pix,c,extent=(xmin,xmax,ymin,ymax))
    else: # else greyscale
      gray()
      imshow(-pix,vmin=-r1,vmax=-r2,extent=(xmin,xmax,ymin,ymax),origin='lower',interpolation='nearest',aspect='auto')

# plot floating labels
  for z in f_label:
    if usetex:
      figtext(z[0],z[1],z[-1],horizontalalignment='left',verticalalignment='top',color=z[2],size=14)
    else:
      figtext(z[0],z[1],z[-1],horizontalalignment='left',verticalalignment='top',color=z[2],size=20)

# set colors and outlyers count
  o1 = o2 = o3 = o4 = 0

# load the points, each set a different color
# from the master array
  for i,data in enumerate(master[abs(igray):]):
    x1=[] ; x2=[] ; y1=[] ; y2=[] ; err_x=[] ; err_y=[]
    for tmp in data:
      if tmp[4] == 0: # 1st array
        x1.append(tmp[0])
        y1.append(tmp[1])
        if ptype[i+abs(igray)][7]:
          err_x.append(tmp[2])
        else:
          err_x.append(0.)
        if ptype[i+abs(igray)][8]:
          err_y.append(tmp[3])
        else:
          err_y.append(0.)
      else: # deletions 2nd array
        x2.append(tmp[0])
        y2.append(tmp[1])
      if tmp[0] > xmax: o1+=1
      if tmp[0] < xmin: o2+=1
      if tmp[1] > ymax: o3+=1
      if tmp[1] < ymin: o4+=1

    axe.set_xlim(xmin,xmax)
    axe.set_ylim(ymin,ymax)

# if dataset ptype[4] = line, plot line, else points
#    print ptype,i,abs(igray)
    if ptype[i+abs(igray)][4]:
      if '-l' in sys.argv:
        h1=[x1[0]] ; h2=[y1[0]]
        for t1,t2 in zip(x1[1:],y1[1:]):
          if t1 < h1[-1]:
            if i == 1: print t1,t2,h1
            axe.plot(h1,h2,ptype[i+abs(igray)][3]+ptype[i+abs(igray)][4])
            h1=[] ; h2=[]
          h1.append(t1) ; h2.append(t2)
        else:
          axe.plot(h1,h2,ptype[i+abs(igray)][3]+ptype[i+abs(igray)][4])
      else:
        axe.plot(x1,y1,ptype[i+abs(igray)][3]+ptype[i+abs(igray)][4])
        axe.set_xlim(xmin,xmax)
        axe.set_ylim(ymin,ymax)
    else:
      if ptype[i+abs(igray)][5] == 0: # ptype = 0, use points; = 1, use labels, = 2, use labels and size of label
        axe.scatter(x1,y1,s=ptype[i+abs(igray)][6]*50,marker=ptype[i+abs(igray)][2],color=ptype[i+abs(igray)][3])
        if x2: axe.scatter(x2,y2,s=ptype[i+abs(igray)][6]*50,marker='x',color=ptype[i+abs(igray)][3])
        if ptype[i+abs(igray)][7] or ptype[i+abs(igray)][8]: 
          for t1,t2,t3,t4 in zip(x1,y1,err_x,err_y):
            axe.errorbar(t1,t2,xerr=t3,yerr=t4,ecolor=ptype[i+abs(igray)][3])
        axe.set_xlim(xmin,xmax)
        axe.set_ylim(ymin,ymax)
      else: # or use labels instead of points
        if ptype[i+abs(igray)][5] == 2:
          imin=1.e33
          imax=-1.e33
          for tmp in data:
            if float(tmp[-1]) < imin: imin=float(tmp[-1])
            if float(tmp[-1]) > imax: imax=float(tmp[-1])
          mz=(8.-24.)/(imin-imax)
          tz=-mz*imin+0.5
          for tmp in data:
            if tmp[4] == 0 and tmp[0] > xmin and tmp[0] < xmax and tmp[1] > ymin and tmp[1] < ymax:
              axe.text(tmp[0],tmp[1],tmp[5],color=ptype[i+abs(igray)][3],horizontalalignment='center', \
                       verticalalignment='center',size=mz*float(tmp[-1]))
        else:
          for tmp in data:
            if tmp[4] == 0 and tmp[0] > min(xmin,xmax) and tmp[0] < max(xmax,xmin) and \
               tmp[1] > min(ymin,ymax) and tmp[1] < max(ymax,ymin):
              axe.text(tmp[0],tmp[1],tmp[5],color=ptype[i+abs(igray)][3],horizontalalignment='center', \
                       verticalalignment='center',size=int(ptype[i+abs(igray)][6]*12))

  if not usetex:
    for nn in range(len(master)):
      ft=figtext(0.95,0.03+nn*0.015,str(len(master[nn])),horizontalalignment='right',verticalalignment='top', \
                 color=ptype[nn][3],size=10)
      figtext(0.91,0.90-nn*0.018,filenames[nn],horizontalalignment='left',verticalalignment='top', \
                 color=ptype[nn][3],size=10)


# plot linear fits if they exist
  try:
    a # a & b = regular fit, ax & bx = biweight fit
    axe.plot([xmin,xmax],[b*xmin+a,b*xmax+a],color='k')
    axe.set_xlim(xmin,xmax)
    axe.set_ylim(ymin,ymax)
    strng='m = '+'%5.4g' % b+' +/- '+'%5.4g' %sigm
    ft=figtext(0.130,0.97,strng,horizontalalignment='left',verticalalignment='top',color='k',size=10)
    strng='b = '+'%5.4g' % a+' +/- '+'%5.4g' %sigb
    ft=figtext(0.130,0.95,strng,horizontalalignment='left',verticalalignment='top',color='k',size=10)
    strng='R = '+'%5.4g' % r
    ft=figtext(0.130,0.93,strng,horizontalalignment='left',verticalalignment='top',color='k',size=10)
    axe.plot([xmin,xmax],[bx*xmin+ax,bx*xmax+ax],color='r')
    xp=xmin+0.38*(xmax-xmin)
    axe.set_xlim(xmin,xmax)
    axe.set_ylim(ymin,ymax)
    strng='m = '+'%5.4g' % bx+' +/- '+'%5.4g' %sigmx
    ft=figtext(0.45,0.97,strng,horizontalalignment='left',verticalalignment='top',color='r',size=10)
    strng='b = '+'%5.4g' % ax+' +/- '+'%5.4g' %sigbx
    ft=figtext(0.45,0.95,strng,horizontalalignment='left',verticalalignment='top',color='r',size=10)
    strng='R = '+'%5.4g' % rx
    ft=figtext(0.45,0.93,strng,horizontalalignment='left',verticalalignment='top',color='r',size=10)
    axe.plot([xmin,xmax],[bz*xmin+az,bz*xmax+az],color='g')
    axe.set_xlim(xmin,xmax)
    axe.set_ylim(ymin,ymax)
    strng='m = '+'%5.4g' % bz
    ft=figtext(0.78,0.97,strng,horizontalalignment='left',verticalalignment='top',color='g',size=10)
    strng='b = '+'%5.4g' % az
    ft=figtext(0.78,0.95,strng,horizontalalignment='left',verticalalignment='top',color='g',size=10)
    strng='deletion sigma = '+'%.2f' % delsig
    ft=figtext(0.72,0.93,strng,horizontalalignment='left',verticalalignment='top',color='g',size=10)
  except:
    pass

# draw manual lines
  for z in lines:
    axe.plot([xmin,xmax],[z[0]*xmin+z[1],z[0]*xmax+z[1]],z[3]+z[2])
  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymin,ymax)

# gluge to find common labeled points
  if cmd == 'D':
    x1=[] ; y1=[]
    for tmp in master[0]:
      if tmp[-1] == line:
        x1.append(tmp[0])
        y1.append(tmp[1])
    axe.plot(x1,y1,'r')
    axe.set_xlim(xmin,xmax)
    axe.set_ylim(ymin,ymax)

# box and label axes
  tick=ticks(axe.xaxis.get_majorticklocs()[0],axe.xaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  axe.xaxis.set_minor_locator(minorLocator)
  tick=ticks(axe.yaxis.get_majorticklocs()[0],axe.yaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  axe.yaxis.set_minor_locator(minorLocator)
  if labels['X'] != 'None': xlabel(labels['X'])
  if labels['Y'] != 'None': ylabel(labels['Y'])
  if labels['T'] != 'None': suptitle(labels['T'])
  ion()
  draw()

def help():
  line='/ = exit                 b = change borders\n'
  line=line+'r = reset                B = select border (with cursor)\n'
  line=line+'h = hardcopy (pick.pdf)  m = draw a line segment\n'
  line=line+'\n'
  line=line+'f = open new file window\n'
  line=line+'F = redraw current files\n'
  line=line+'p = open plot style window\n'
  line=line+'e = plot error bars\n'
  line=line+'X,Y,T = activate titles window\n'
  line=line+'w = activate labels window\n'
  line=line+'\n'
  line=line+'t = toggle labels\n'
  line=line+'s = scale size of points/labels\n'
  line=line+'u = use label as size for points\n'
  line=line+'\n'
  line=line+'g = grayscale          c = contrast control\n'
  line=line+'n = normalized gray    z = contour plot\n'
  line=line+'\n'
  line=line+'l = linear fit (rotates through datasets)\n'
  line=line+'x,1,2,3,4 = delete points (individual, quads)\n'
  line=line+'d = delete sigma from fit, each hit lowers sigma\n'
  line=line+'\n'
  line=line+'o = output points into ok (pick.ok)\n'
  line=line+'    and deletion files (pick.dels)\n'
  p = subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -text_window', \
                       shell=True, stdin=subprocess.PIPE)
  p.communicate(line)

#def get_string(event): # event routine to get strings
#  global axe,xmin,xmax,ymin,ymax,line,cmd,cid1,cid2,ft,master,ifile,box,pix,igray,r1,r2,ifit,f_label,filenames,ptype
#  print 'cid2 key',event.key,'cmd',cmd,'line',line
#
#  if event.key == 'l':
#    axe.set_xscale('linear') ; axe.set_yscale('linear') ; draw()
#  if event.key == 'g':
#    axe.grid(False) ; draw()
#
#  if event.key == 'enter': # <cr> disconnect, reconnect primary clicker, do action
#    disconnect(cid2)
#    action()
#    draw_x(False)
#    cid1=connect('key_press_event',clicker)
#
#  elif event.key == 'backspace': # delete characters, stop at 0 or ': '
#    try:
#      if line[-2:] != ': ': line=line[:-1]
#    except:
#      pass
#
#  elif event.key in [None,'shift','control','alt','right','left','up','down','escape']: # ignore weird keys
#    pass
#
#  else:
#    if event.key == 'L':
#      line=line+'l'
#    elif event.key =='G':
#      line=line+'g'
#    else:
#      line=line+event.key
#
#  try:
#    fig.texts.remove(ft) # remove the line for redraw
#  except:
#    pass
#
#  ft=figtext(0.1,0.05,line,horizontalalignment='left',verticalalignment='top') # type the line at

#def action(): # do the actions from clicker as given by var cmd
#  global xmin,xmax,ymin,ymax,line,cmd,cid1,cid2,ft,master,ifile,box,pix,igray,r1,r2,ifit,f_label,filenames,ptype
#
#  try:
#    pass
#  except:
#    fig.texts.remove(ft)
#    ft=figtext(0.1,0.05,'INPUT ERROR',horizontalalignment='left',verticalalignment='top',color='r')
#    time.sleep(2)
#
#  line=''
#  return

def clicker(event): # primary event handler
  global switch,axe,xmin,xmax,ymin,ymax,line,cmd,cid1,cid2,ft,master,ifile,box,pix,igray,r1,r2,ifit,label,dx,dy,f_label,filenames,ptype,lines
  global a,b,r,sigb,sigm,sig,ax,bx,rx,sigbx,sigmx,sigx,az,bz,delsig,sigma
#  print 'cid1 key',event.key,'cmd',cmd,'line',line,xmin,xmax,ymin,ymax

  cmd=event.key

  ioff()

  if event.key in ['/','q']:
    disconnect(cid1)
    close('all')
    time.sleep(0.5)
    sys.exit()

  if cmd in ['i','D']:
    rmin=1.e33
    for i,tmp in enumerate(master[0]):
      r=((event.xdata-tmp[0])**2+(event.ydata-tmp[1])**2)**0.5
      if r < rmin:
        rmin=r
        imin=i
    line=master[0][imin][-1]
    if cmd == 'i': print master[0][imin]

  elif cmd == 'o':
    filout1=open('pick.oks','w')
    filout2=open('pick.del','w')
    for i,data in enumerate(master[abs(igray):]):
      for tmp in data:
        if not tmp[4]:
          for t in tmp:
            filout1.write(str(t)+' ')
          filout1.write('\n')
        else:
          for t in tmp:
            filout2.write(str(t)+' ')
          filout2.write('\n')
    filout1.close()
    filout2.close()

  elif cmd == '?':
    help()

  elif cmd == 't': # toggle labels,points
    for t in range(len(ptype)):
      ptype[t][5]=abs(ptype[t][5]-1)

  elif cmd == 's': # scale the labels,points
    for t in range(len(ptype)):
      ptype[t][6]=ptype[t][6]*(event.xdata*1.5/(xmax-xmin)+0.5-1.5*xmin/(xmax-xmin))

  elif cmd == 'c':
    k=0.5+(event.xdata-xmin)/(xmax-xmin)
    try:
      r1=r1*k
    except:
      r1=0.
    r2=0.
    c=arange(r2,r1,(r1-r2)/10.) # set contour levels and/or contrast

  elif cmd in ['x','1','2','3','4']:
    rmin=1.e33
    tank=[]
    if ifit == 1 or ifit == 0:
      itest=0
    else:
      itest=ifit-1
    for i,data in enumerate(master):
      if i == itest:
        for n,tmp in enumerate(data):
          r=(((event.xdata-tmp[0])/(xmax-xmin))**2+((event.ydata-tmp[1])/(ymax-ymin))**2)**0.5
          if r <= rmin:
            rmin=r
            imin=n
          if cmd == '1' and tmp[0] > event.xdata and tmp[1] > event.ydata: data[n][4]=abs(data[n][4]-1)
          if cmd == '2' and tmp[0] < event.xdata and tmp[1] > event.ydata: data[n][4]=abs(data[n][4]-1)
          if cmd == '3' and tmp[0] < event.xdata and tmp[1] < event.ydata: data[n][4]=abs(data[n][4]-1)
          if cmd == '4' and tmp[0] > event.xdata and tmp[1] < event.ydata: data[n][4]=abs(data[n][4]-1)
        if cmd == 'x': data[imin][4]=abs(data[imin][4]-1)
      tank.append(data)
    master=tank

  elif event.key == 'd':
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
    except:
      pass

  elif event.key in ['X','Y','T']:
    line='0 1:\nlabels: values\n7 20\nx_label '+labels['X']+'\ny_label '+labels['Y']+'\ntitle '+labels['T']+'\n'
    p = subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -entry_field -noadd', \
                         shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=p.communicate(line)[0]
    if '>>>aborting<<<' not in tmp:
      for t,z in zip(['X','Y','T'],tmp.split('\n')[:-1]):
        try:
          labels[t]=z.split(':')[-1].lstrip()
        except:
          labels[t]=''

  elif event.key == 'w':
    line='0 1 2 3:\nx y color plot label\n3 3 5 15\n'
    for z in f_label:
      for t in z[:-1]:
        line=line+str(t)+' '
      line=line+z[-1]+'\n'
    p = subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -entry_field', \
                         shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=p.communicate(line)[0]
    if '>>>aborting<<<' not in tmp:
      f_label=[]
      for t in tmp.split('\n')[:-1]:
        f_label.append([float(t.split()[0]),float(t.split()[1]),t.split()[2],' '.join(t.split()[3:])])

  elif cmd in ['f','p','F']:
    if cmd != 'F':
      line='0 1 2 3 4 5 6 7 8 9\nfile xcol ycol pstyle color lstyle label scale err_x err_y\n10 4 4 6 6 6 6 6 6 6\n'
    else:
      line=''
    for t,z in zip(filenames,ptype):
      line=line+t+' '+str(z[0])+' '+str(z[1])+' '+ \
                 str(z[2][0])+','+str(z[2][1])+','+str(int(180*z[2][2]/math.pi))+' '+ \
                 z[3]+' '+str(z[4])+' '+str(z[5])+' '+'%.1f' % (z[6])+' '+str(z[7])+' '+str(z[8])+'\n'
    if cmd in ['f','F']:
      line=line+'None '+str(ptype[-1][0])+' '+str(ptype[-1][1])+' '+ \
                 str(ptype[-1][2][0])+','+str(ptype[-1][2][1])+','+str(int(180*ptype[-1][2][2]/math.pi))+' '+ \
                 colors[min(ifile+1,6)]+' '+str(ptype[-1][4])+' '+str(ptype[-1][5])+' '+'%.1f' % (ptype[-1][6])+' '+ \
                 str(ptype[-1][7])+' '+str(ptype[-1][8])+'\n'
      if cmd == 'f':
        p = subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -entry_field', \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
      else:
        tmp=line
    else:
      p = subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -entry_field -noadd', \
                         shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    if cmd != 'F': tmp=p.communicate(line)[0]
    if '>>>aborting<<<' not in tmp:
      ptype=[]
      ifile=-1
      filenames=[]
      master=[]
      for line in tmp.split('\n')[:-1]:
        if 'None' not in line:
          try:
            file=open(line.split()[0],'r')
            i=int(line.split()[1])
            j=int(line.split()[2])
            filenames.append(line.split()[0])
            data=[]
            while 1:
              tmp=file.readline()
              if not tmp or len(tmp) < 2: break
              try:
                data.append([float(tmp.split()[i]),float(tmp.split()[j]),float(tmp.split()[int(line.split()[8])]),
                             float(tmp.split()[int(line.split()[9])]),0,tmp.split()[-1]])
              except:
                try:
                  data.append([float(tmp.split()[i]),float(tmp.split()[j]),0.,0.,0,tmp.split()[-1]])
                except:
                  pass
            master.append(data)
            ifile+=1
            file.close()
          except:
            print 'file error'
          junk=[]
          junk.append(i)
          junk.append(j)
          junk.append((int(line.split()[3].split(',')[0]), \
                          int(line.split()[3].split(',')[1]), \
                          math.pi*float(line.split()[3].split(',')[2])/180.))
          junk.append(line.split()[4])
          if line.split()[5] == '0':
            junk.append(0)
          else:
            junk.append(line.split()[5])
          junk.append(int(line.split()[6]))
          junk.append(float(line.split()[7]))
          junk.append(int(line.split()[8]))
          junk.append(int(line.split()[9]))
          ptype.append(junk)
   
      if not abs(igray):
        try:
          switch
        except:
          x=[] ; y=[] ; xmin=ymin=1.e33 ; xmax=ymax=-1.e33
          for w in master:
            for z in w:
              x.append(z[0])
              y.append(z[1])

            t1,t2,t3,t4=min_max(x,y)
            if t1 < xmin: xmin=t1
            if t2 > xmax: xmax=t2
            if t3 < ymin: ymin=t3
            if t4 > ymax: ymax=t4

  elif event.key in ['m']: # enter manual lines
    line='0 1 2 3\nslope zpt color lstyle\n6 6 6 6\n'
    if not lines:
      line=line+'1 0 b -\n'
    else:
      for t in lines:
        line=line+str(t[0])+' '+str(t[1])+' '+t[2]+' '+t[3]+'\n'
    p = subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -entry_field', \
                         shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=p.communicate(line)[0]
    if '>>>aborting<<<' not in tmp:
      lines=[]
      for t in tmp.split('\n')[:-1]:
        lines.append([float(t.split()[0]),float(t.split()[1]),t.split()[2],t.split()[3]])

  elif event.key in ['b']: # enter borders
    switch=1 # set switch so new files don't change borders
    line='0 1 2 3\nxmin xmax ymin ymax\n5 5 5 5\n'+str(xmin)+' '+str(xmax)+' '+str(ymin)+' '+str(ymax)+'\n'
    p = subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -entry_field -noadd', \
                         shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=p.communicate(line)[0]
    if '>>>aborting<<<' not in tmp:
      xmin,xmax,ymin,ymax=map(float,tmp.split('\n')[:-1][0].split())

  elif event.key in ['g','n','z']: # build array for grayscale
    box=int(box*2.) # box size for binning, reduce each time
    igray=1         # set grayscale switch
    dx=(xmax-xmin)/box
    dy=(ymax-ymin)/box
    pix=zeros((box,box),'Float32')
    r1=0. ; r2=0.

    if event.key == 'g':
      for jj,y in enumerate(arange(ymin,ymax,dy)):
        for ii,x in enumerate(arange(xmin,xmax,dx)):
          n=0.
          for t in master[ifit]:
            if t[0] >= x and t[0] < x+dx and t[1] >= y and t[1] < y+dy: n+=1
          pix[jj][ii]=n # load up array
          if n > r1: r1=n+2

    if event.key == 'n':
      out=open('pick.tmp','w')
      for t in master[ifit]:
        out.write(str(t[0])+' '+str(t[1])+'\n')
      out.close()
      tmp=os.popen('build_norm pick.tmp '+str(xmin)+' '+str(xmax)+' '+str(ymin)+' '+str(ymax)+' '+str(box)).read()
      os.system('rm pick.tmp')
      for jj,t in enumerate(tmp.split('\n')):
        for ii,n in enumerate(t.split()):
          pix[jj][ii]=float(n)
          if float(n) > r1: r1=float(n)+2

    if event.key == 'z': # for a contour
      igray=-1
      c=array(arange(r2,r1,(r1-r2)/10.))

  elif event.key == 'l': # linear fit
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

    tx=(by*ax+ay)/(1.-by*bx) # find mean slope and intercept for independent fit
    ty=bx*tx+ax
    bz=(bx+1./by)/2.
    az=ty-bz*tx

    ifit=ifit+1 # loop through files to fit
    if ifit == len(master): ifit=0

  elif event.key == 'r': # reset parameters
    igray=0 ; x=[] ; y=[] ; box=5. ; ifit=0
    for w in master:
      for z in w:
        x.append(z[0])
        y.append(z[1])
    xmin,xmax,ymin,ymax=min_max(x,y)

  elif event.key == 'h': # postscript hardcopy
    fig.set_size_inches((8,8))
    draw_x(True)
    fig.savefig('pick.pdf')
#    draw_x(True)
#    fig.savefig('pick.ps')
    if 'deepcore' in os.uname()[1] and '-tex' not in sys.argv:
      fig.set_size_inches((12,12))
    elif '-tex' in sys.argv:
      fig.set_size_inches((8,8))
    else:
      fig.set_size_inches((9,9))
    draw_x(False)
    ft=figtext(0.1,0.05,'output to pick.pdf',horizontalalignment='left',verticalalignment='top',color='r')
    time.sleep(2)

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

#  elif event.key == 'backspace':
#    try:
#      if line[-2:] != ': ': line=line[:-1]
#    except:
#      pass

#  if event.key in ['m']:
#    ft=figtext(0.1,0.05,line,horizontalalignment='left',verticalalignment='top')
#    disconnect(cid1)
#    cid2=connect('key_press_event',get_string)
#  elif event.key not in [None,'shift','control','alt','right','left','up','down','escape']:
#    draw_x(False)

  ion()

  if event.key not in ['shift']:
    draw_x(False)

#main

if len(sys.argv) <= 1 or sys.argv[1] == '-h':
  print 'Usage: pick op filename xcol ycol'
  print
  print '>>> not-so-quick plotting script <<<'
  print
  print 'file needs x,y points in any column, but labels'
  print 'need to be in the last column.  If filename has'
  print '"*" in it, reads all those files'
  print
  print 'Options:  -b = start borders (x1,x2,y1,y2)'
  print '          -p = style arrays'
  print '          -t = enter title dictionary'
  print '          -l = don\'t connect endpoints'
  print
  print 'interactive controls'
  print '--------------------------------------------------------'
  print '/ = exit                 b = change borders'
  print 'r = reset                B = select border (with cursor)'
  print 'h = hardcopy (pick.pdf)  m = draw a line segment'
  print
  print 'f = open new file window p = open plot style window'
  print 'e = plot error bars      w = activate labels window'
  print 'X,Y,T = activate titles window'
  print
  print 't = toggle labels        s = scale size of points/labels'
  print 'u = use label as size for points'
  print
  print 'g = grayscale            c = contrast control'
  print 'n = normalized gray      z = contour plot'
  print
  print 'l = linear fit (rotates through datasets)'
  print 'x,1,2,3,4 = delete points (individual, quads)'
  print 'd = delete sigma from fit, each hit lowers sigma'
  print
  print 'o = output points into ok (pick.ok)'
  print '    and deletion files (pick.dels)'
  sys.exit()

# look for column numbers in sys.argv
try:
  if '-b' in sys.argv:
    switch=1
    i=int(sys.argv[2])
    j=int(sys.argv[3])
  else:
    i=int(sys.argv[-2])
    j=int(sys.argv[-1])
except:
  i=0
  j=1

master=[] ; filenames=[] ; ptype=[] ; x=[] ; y=[] ; data=[]   # initialize master list
ifile=-1                                       # color type
colors=['k','r','g','b','c','m','y']

# look for filenames in sys.argv

for z in sys.argv[1:]:
  if not z.isdigit() and '[' not in z and z != '-l':
    try:
      float(z)
    except:
      filenames.append(z)

if '-p' in sys.argv:
  ptype=[]
  for z in sys.argv:
    if '[' in z:
      ptype.append(eval(z))

for file in filenames:
  if file in ['-p','-b','-sfb']: break
  ifile+=1
#  print 'loading ...',file,'('+colors[ifile]+')'
  try:
    input=open(file,'r')
  except:
    print 'file name',file,'not found'
    sys.exit()
  data=[]
  while 1:
    line=input.readline()
    if not line or len(line) < 2: break
    if '-p' in sys.argv:
      i=ptype[ifile][0]
      j=ptype[ifile][1]
      e1=ptype[ifile][-2]
      e2=ptype[ifile][-1]
    else:
      e1=i+2
      e2=i+3
    try:
      x.append(float(line.split()[i]))
      y.append(float(line.split()[j]))
    except:
      pass
    try:
      data.append([float(line.split()[i]),float(line.split()[j]),float(line.split()[e1]),
                   float(line.split()[e2]),0,line.split()[-1]])
    except:
      try:
        data.append([float(line.split()[i]),float(line.split()[j]),0.,0.,0,line.split()[-1]])
      except:
        pass
  master.append(data)
  if '.line' in file: # look at file name to determine ptype
    ptype.append([i,j,(6,2,0),colors[ifile],'-',0,1.,0,0])
  elif '.dash' in file:
    ptype.append([i,j,(6,2,0),colors[ifile],'--',0,1.,0,0])
  else:
    ptype.append([i,j,(6,2,0),colors[ifile],0,0,1.,0,0])
  input.close()

# data read in as
# 0,1: x and y in input i and j columns
# 2,3: errorbars for x and y, assumed to be in column i+2 and i+3 of raw data
# 4: kill for linear fitting
# 5: label assumed to be in last column of data file
# label found, not errorbars

# initialize parameters
delsig=3.0                        # deletion sigma for linfit
ifit=0                            # which set used for linfit
igray=0                           # greyscale flag
box=5.                            # size of greyscale/contour bin
f_label=[]                        # floating labels
lines=[]                          # line marks
labels={'X':'None','Y':'None','T':'None'}     # axis labels
line=''
cmd=None

xmin,xmax,ymin,ymax=min_max(x,y)  # set boundaries
if '-sfb' in sys.argv:
  tmp=ymin
  ymin=ymax
  ymax=tmp
  switch=1

if '-t' in sys.argv:
  labels=eval(sys.argv[sys.argv.index('-t')+1])

if '-b' in sys.argv:
  xmin=float(sys.argv[sys.argv.index('-b')+1])
  xmax=float(sys.argv[sys.argv.index('-b')+2])
  ymin=float(sys.argv[sys.argv.index('-b')+3])
  ymax=float(sys.argv[sys.argv.index('-b')+4])

from Tkinter import Tk
w=Tk()
s_width=w.winfo_screenwidth()
s_height=w.winfo_screenheight()
w.destroy()

geo=eval(' '.join([tmp[:-1] for tmp in open(os.environ['ARCHANGEL_HOME']+'/.archangel','r').readlines()]))
fig_size=int(geo['main_size'])
if '-tex' in sys.argv: fig_size=8

fig = figure(figsize=(fig_size, fig_size), dpi=80)  # initialize plot parameters
axe = fig.add_subplot(111)  # assign axe for text and axes
manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
manager.window.title('')
manager.window.geometry(geo['main_window'])
#rc('font',**{'family':'serif','sans-serif':['Times New Roman']})
#rc('text',usetex=True)

if '-hard' in sys.argv:
  draw_x(True)
  fig.savefig(sys.argv[-1])
  sys.exit()
else:
  if '-tex' in sys.argv:
    fig.set_size_inches((8,8))
    draw_x(True)
  else:
    draw_x(False)

cid1=connect('key_press_event',clicker)
show()
