#!/usr/bin/env python

import pyfits,sys,os,time,subprocess,signal
from math import *
from xml_archangel import *
from pylab import *
from matplotlib.ticker import MultipleLocator # needed to fix up minor ticks
from matplotlib.patches import Ellipse, Polygon

# core display program 

def help():
  return '''
Usage: display option master_file

quick grayscale display GUI

options: -c = contrast values r1 & r2
     -color = run with jet colormap
       -win = change default window (size+xw+yw)
       -z N = start with zoom factor N (default=2)
              or i1,i2,i3,i4 for pixel corners

cursor commands:

/ = abort/move to next image      q = quit
z = zoom                          Z = recenter
r = unzoom                        R = reset zoom                    
c = contrast                      m = manual contrast values
v = invert grayscale              G = make snap of current image
L = make hardcopy of current frame
p = peek at values                '''

def get_data():
  global pix,nx,ny,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,filename
  global pix2,i1b,i2b,j1b,j2b,r1b,r2b,middleb,xsky2,skysig2,filename2
  global ax,ft,cid,pids,geo,last_cmd,cmd,xstep,blink1,blink2,blink3,iv,iblink,dels

  try: # test for file existance and get header information
    fitsobj=pyfits.open(filename,"readonly")
  except:
    print filename,'not found -- ABORTING'
    return

  nx=fitsobj[0].header['NAXIS1']
  ny=fitsobj[0].header['NAXIS2']
  pix=fitsobj[0].data # read the pixels
  fitsobj.close()

  try: # read xml file with xml_archangel classes
    doc = minidom.parse(filename.split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)
  except:
    pass

  try: # sky and sky sigma values
    xsky=float(elements['sky'][0][1])
    skysig=float(elements['skysig'][0][1])
  except: # if no sky, get a 1st guess
    if nx < 50:
      go_cmd='sky_box -s '+filename
    else:
      go_cmd='sky_box -f '+filename
    tmp=os.popen(go_cmd).read()
    if len(tmp) < 1 or 'error' in tmp: # try a full sky search
      go_cmd='sky_box -s '+filename
      tmp=os.popen(go_cmd).read()
      if len(tmp) < 1 or 'error' in tmp:
        print 'error in figuring out sky, aborting'
        sys.exit()
    xsky=float(tmp.split()[2])
    skysig=float(tmp.split()[3])

  sig=100.
  r1=xsky+sig*skysig
  r2=xsky-0.05*(r1-xsky)
  middle=xsky
  zx=64
  iblink=0 ; dels=[]
  xstep=nx/zx
  i1=int(blink3[0][0]-nx/zx)
  i2=int(blink3[0][0]+nx/zx)
  j1=int(blink3[0][1]-nx/zx)
  j2=int(blink3[0][1]+nx/zx)

  try: # test for file existance and get header information
    fitsobj=pyfits.open(filename2,"readonly")
  except:
    print filename2,'not found -- ABORTING'
    return

  nx=fitsobj[0].header['NAXIS1']
  ny=fitsobj[0].header['NAXIS2']
  pix2=fitsobj[0].data # read the pixels
  fitsobj.close()

  try: # read xml file with xml_archangel classes
    doc = minidom.parse(filename2.split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)
  except:
    pass

  try: # sky and sky sigma values
    xsky2=float(elements['sky'][0][1])
    skysig2=float(elements['skysig'][0][1])
  except: # if no sky, get a 1st guess
    if nx < 50:
      go_cmd='sky_box -s '+filename2
    else:
      go_cmd='sky_box -f '+filename2
    tmp=os.popen(go_cmd).read()
    if len(tmp) < 1 or 'error' in tmp: # try a full sky search
      go_cmd='sky_box -s '+filename2
      tmp=os.popen(go_cmd).read()
      if len(tmp) < 1 or 'error' in tmp:
        print 'error in figuring out sky, aborting'
        sys.exit()
    xsky2=float(tmp.split()[2])
    skysig2=float(tmp.split()[3])

  r1b=xsky2+sig*skysig2
  r2b=xsky2-0.05*(r1-xsky2)
  middleb=xsky2
  xstep=nx/zx
  i1b=int(blink3[0][2]-nx/zx)
  i2b=int(blink3[0][2]+nx/zx)
  j1b=int(blink3[0][3]-nx/zx)
  j2b=int(blink3[0][3]+nx/zx)

  iv=-1     # sky is white, objects black

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
  global pix,nx,ny,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,filename
  global pix2,i1b,i2b,j1b,j2b,r1b,r2b,middleb,xsky2,skysig2,filename2
  global ax,ft,cid,pids,geo,last_cmd,cmd,xstep,blink1,blink2,blink3,iv,iblink,dels

  clf() ; ax = fig.add_subplot(111)

  ax = axes([0.05,0.05,0.45,0.95])

  zm=ma.masked_where(isnan(pix[j1-1:j2,i1-1:i2]), pix[j1-1:j2,i1-1:i2])
  if '-color' in sys.argv:
    palette=cm.jet
    imshow(-iv*zm,vmin=r2,vmax=r1,extent=(i1-0.5,i2+0.5,j1-0.5,j2+0.5), \
           aspect='equal',origin='lower',interpolation='nearest',cmap=palette)
  else:
    palette=cm.gray
    palette.set_bad('r', 1.0)
    imshow(iv*zm,vmin=-r1,vmax=-r2,extent=(i1-0.5,i2+0.5,j1-0.5,j2+0.5), \
           aspect='equal',origin='lower',interpolation='nearest',cmap=palette)

  tick=ticks(ax.xaxis.get_majorticklocs()[0],ax.xaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  ax.xaxis.set_minor_locator(minorLocator)
  tick=ticks(ax.yaxis.get_majorticklocs()[0],ax.yaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  ax.yaxis.set_minor_locator(minorLocator)
#  ft=figtext(0.13,0.93,'%.2f' % r2,horizontalalignment='left',verticalalignment='top',color='b')

  tmp=[]
  for t in blink1:
    if t[0] > i1 and t[0] < i2 and t[1] > j1 and t[1] < j2: tmp.append(t)
  ells=[Ellipse((t[0],t[1]),10.,10.,0.,fill=0) for t in tmp]
  for e in ells:
    e.set_clip_box(ax.bbox)
    e.set_alpha(1.0)
    e.set_edgecolor('b')
    ax.add_artist(e)

  ells=[Ellipse((blink3[iblink][0],blink3[iblink][1]),5.,5.,0.,fill=0)]
  for e in ells:
    e.set_clip_box(ax.bbox)
    e.set_alpha(1.0)
    e.set_edgecolor('r')
    ax.add_artist(e)

  ax = axes([0.53,0.05,0.45,0.95])

  zm=ma.masked_where(isnan(pix2[j1b-1:j2b,i1b-1:i2b]), pix2[j1b-1:j2b,i1b-1:i2b])
  if '-color' in sys.argv:
    palette=cm.jet
    imshow(-iv*zm,vmin=r2,vmax=r1,extent=(i1-0.5,i2+0.5,j1-0.5,j2+0.5), \
           aspect='equal',origin='lower',interpolation='nearest',cmap=palette)
  else:
    palette=cm.gray
    palette.set_bad('r', 1.0)
    imshow(iv*zm,vmin=-r1b,vmax=-r2b,extent=(i1b-0.5,i2b+0.5,j1b-0.5,j2b+0.5), \
           aspect='equal',origin='lower',interpolation='nearest',cmap=palette)

  tick=ticks(ax.xaxis.get_majorticklocs()[0],ax.xaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  ax.xaxis.set_minor_locator(minorLocator)
  tick=ticks(ax.yaxis.get_majorticklocs()[0],ax.yaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  ax.yaxis.set_minor_locator(minorLocator)

  tmp=[]
  for t in blink2:
    if t[0] > i1b and t[0] < i2b and t[1] > j1b and t[1] < j2b: tmp.append(t)
  ells=[Ellipse((t[0],t[1]),10.,10.,0.,fill=0) for t in tmp]
  for e in ells:
    e.set_clip_box(ax.bbox)
    e.set_alpha(1.0)
    e.set_edgecolor('g')
    ax.add_artist(e)

  ells=[Ellipse((blink3[iblink][2],blink3[iblink][3]),5.,5.,0.,fill=0)]
  for e in ells:
    e.set_clip_box(ax.bbox)
    e.set_alpha(1.0)
    e.set_edgecolor('r')
    ax.add_artist(e)

  print iblink,blink3[iblink]
  draw()

def kill_pids(pids,kill_all):
  tmp=[]
  for z in pids:
    try:
      if z[1] or kill_all:
        os.system('rm '+z[2])
        os.kill(z[0],signal.SIGKILL) # god knows why the rxvt shell is pid+1, original shell is gone
      else:
        tmp.append(z)
    except:
      tmp.append(z)
  return tmp

def clicker(event): # primary event handler
  global pix,nx,ny,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,filename
  global pix2,i1b,i2b,j1b,j2b,r1b,r2b,middleb,xsky2,skysig2,filename2
  global ax,ft,cid,pids,geo,last_cmd,cmd,xstep,blink1,blink2,blink3,iv,iblink,dels

  ioff()

  cmd=event.key

  try:
    ix=int(round(event.xdata))
    iy=int(round(event.ydata))
  except:
    ix=0
    iy=0

  if event.key in ['/','q']:
    disconnect(cid)
    close()
    out=open('blink.good','w')
    for n,line in enumerate(blink3):
      if n not in dels: out.write(' '.join([str(dum) for dum in line])+'\n')
    out.close()
    out=open('blink.bad','w')
    for n,line in enumerate(blink3):
      if n in dels: out.write(' '.join([str(dum) for dum in line])+'\n')
    out.close()
    if pids:
      pids=kill_pids(pids,0)
    time.sleep(0.5) # gluge to catch '/' before it passes it to nearest xwindow
    sys.exit()

  elif event.key in [None,'control','alt','right','left','escape']:
    pass

  elif event.xdata == None or event.ydata == None:
    pass

  elif event.key == '?':
    fout=open('probe_data.tmp','w')
    fout.write(help()+'\n')
    fout.close()
    subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -text_window -x -f probe_data.tmp &',shell=True)

  elif event.key in ['m','n']:
    if event.key == 'n': dels.append(iblink)
#    print 'iblink',iblink
    iblink=iblink+1
    zx=64
    try:
      i1=int(blink3[iblink][0]-nx/zx)
      i2=int(blink3[iblink][0]+nx/zx)
      j1=int(blink3[iblink][1]-nx/zx)
      j2=int(blink3[iblink][1]+nx/zx)
      i1b=int(blink3[iblink][2]-nx/zx)
      i2b=int(blink3[iblink][2]+nx/zx)
      j1b=int(blink3[iblink][3]-nx/zx)
      j2b=int(blink3[iblink][3]+nx/zx)
    except:
      disconnect(cid)
      close()
      out=open('blink.good','w')
      for n,line in enumerate(blink3):
        if n not in dels: out.write(' '.join([str(dum) for dum in line])+'\n')
      out.close()
      out=open('blink.bad','w')
      for n,line in enumerate(blink3):
        if n in dels: out.write(' '.join([str(dum) for dum in line])+'\n')
      out.close()
      if pids:
        pids=kill_pids(pids,0)
      time.sleep(0.5) # gluge to catch '/' before it passes it to nearest xwindow
      sys.exit()

  elif event.key == 'R':
    igrow=0
    xsig=5.
    xstep=nx/2
    i1=1
    i2=nx
    j1=1
    j2=ny
    sky=[]
    if pids: pids=kill_pids(pids,1)

  elif event.key == 'v':
    iv=-iv

  elif event.key == 'c':
    rold=r1
    k=0.5+(event.xdata-i1)/(i2-i1)
    r1=r1*k
    if r1 < middle: r1=(rold-middle)/2.+middle
    r2=middle-0.05*(r1-middle)

  elif event.key == 'p':
    if event.key != last_cmd:
      pids=kill_pids(pids,0)
      file=str(int(time.time()))+'_peek.tmp'
    else:
      for t in pids:
        if 'peek' in t[-1]: file=t[-1]

    fout=open(file,'w')
    fout.write('12\n')
    x1=max(int(round(event.xdata))-4,1)
    x2=min(int(round(event.xdata))+5,nx+1)
    y1=max(int(round(event.ydata))-5,0)
    y2=min(int(round(event.ydata))+4,ny)
    print >> fout,''
    print >> fout,'    ',
    for i in xrange(x1,x2): print >> fout,'%7.1i' % (i),
    print >> fout,''
    for j in xrange(y2,y1,-1):
      print >> fout,'%5.1i' % (j),
      for i in xrange(x1,x2):
        print >> fout,'%7.1f' % pix[j-1,i-1],
      print >> fout,''
    print >> fout,''
    fout.close()

    if event.key != last_cmd:
      p=subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/tterm.py -f magenta -r 13 -c 80 '+ \
        '-p '+geo['peek_window']+' '+os.environ['ARCHANGEL_HOME']+'/util/monitor.py '+file,shell=True)
      pids.append([p.pid+2,1,file])

  elif event.key in ['z','Z','r']:
    if event.key == 'z' and xstep > 4.: xstep=int(xstep/2)+1
    if event.key == 'r': xstep=int(2.*xstep)-1
    if xstep > nx/2:
      xstep=nx/2
      i1=1
      i2=nx
      j1=1
      j2=ny
    else:
      i1=int(round((event.xdata)-xstep)+1)
      i2=int(round((event.xdata)+xstep)+1)
      if i1 < 1:
        i1=1
        i2=int(2*xstep+i1)
      if i2 > nx:
        i1=max(1,int(nx-2*xstep))
        i2=nx
      j1=int(round((event.ydata)-xstep))
      j2=int(round((event.ydata)+xstep))
      if j1 < 1:
        j1=1
        j2=int(2*xstep+j1)
      if j2 > ny:
        j1=int(ny-2*xstep)
        j2=ny

  if event.key not in ['x','s','shift'] or igrow or imarks: 
    draw_image()

  last_cmd=event.key
  ion()

# main

if len(sys.argv) <= 1 or sys.argv[1] == '-h':
  print help()
  sys.exit()

geo=eval(' '.join([tmp[:-1] for tmp in open(os.environ['ARCHANGEL_HOME']+'/.archangel','r').readlines()]))

# format for manual window override 10:+700+25

if '-win' in sys.argv:
  geo['main_size']=sys.argv[sys.argv.index('-win')+1].split('+')[0]
  geo['main_window']='+'+sys.argv[sys.argv.index('-win')+1].split('+')[1]+'+'+sys.argv[sys.argv.index('-win')+1].split('+')[2]

fig_size=int(geo['main_size'])
fig = figure(figsize=(21, 10), dpi=80)
ax = fig.add_subplot(111)
try:
  manager = get_current_fig_manager()
  manager.window.title('')
  manager.window.geometry(geo['main_window'])
except:
  pass

pids=[]
cmd=None ; last_cmd=None

filename=sys.argv[-2]
filename2=sys.argv[-1]
if '.' not in filename: filename=filename.replace('.','')+'.fits'
if '.' not in filename2: filename2=filename2.replace('.','')+'.fits'

# x,y coords of primary filter
# blue for other targets in primary filter
blink1=[(map(float, tmp.split())) for tmp in open(filename.replace('fits','tmp'),'r').readlines()]
# x,y, coords of objects in 2nd filter, objects as green
blink2=[(map(float, tmp.split())) for tmp in open(filename2.replace('fits','tmp'),'r').readlines()]
# red for comparison target in primary filter, red for position in 2nd filter
# compare file has x,y for primary, transformed x,y for 2nd filter
blink3=[(map(float, tmp.split())) for tmp in open('compare.tmp','r').readlines()]

gray()
get_data()
draw_image()

cid=connect('key_press_event',clicker)
show()
