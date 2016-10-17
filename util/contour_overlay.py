#!/usr/bin/env python

import pyfits,sys,os,time,subprocess,signal
from math import *
from xml_archangel import *
from pylab import *
from matplotlib.ticker import MultipleLocator # needed to fix up minor ticks
from matplotlib.patches import Ellipse, Polygon

# quick display program ala prf_edit, enter a list of files or -f image
# first look for profile.py routine, aborts or output new options

def help():
  return '''
Usage: contour_overlay option master_file

quick grayscale display GUI'''

def get_data():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,r3,r4,middle,xsky,skysig,csky,cskysig,sig,filename,nmast,xd,yd,inv,Z,ct
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap
  global ft,cid,channel,markp,pids,geo,last_cmd,cmd,last_peek
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy,rx

  clean=0    
  try: # test for file existance and get header information
    fitsobj=pyfits.open(filename,"readonly")
  except:
    print filename,'not found -- ABORTING'
    return
  nx=fitsobj[0].header['NAXIS1']
  ny=fitsobj[0].header['NAXIS2']
  hdr=fitsobj[0].header

  try: # find coordinate transformations
    if 'POSSII' in hdr['SURVEY']:
      pssii=1
      equinox=2000.
  except:
    pssii=0
  try:
    if 'Palomar 48-in' in hdr['TELESCOP']:
      pssii=1
      equinox=2000.
  except:
    pssii=0

  try:
    trans=[hdr['CRVAL1'],hdr['CRPIX1'],hdr['CDELT1'], \
           hdr['CRVAL2'],hdr['CRPIX2'],hdr['CDELT2']]
    equinox=hdr['EQUINOX']
  except:
    pass
  try:
    trans=[hdr['CRVAL1'],hdr['CRPIX1'],hdr['CD1_1'],hdr['CD1_2'], \
           hdr['CRVAL2'],hdr['CRPIX2'],hdr['CD2_1'],hdr['CD2_2']]
    equinox=hdr['EQUINOX']
  except:
    pass

  pix=fitsobj[0].data # read the pixels

  try: # try and get some basic photometry information
    exptime=fitsobj[0].header['EXPTIME']
    filter=fitsobj[0].header['FILTERS']
    airmass=fitsobj[0].header['AIRMASS']
  except:
    pass

  fitsobj.close()

  prf=None   # ellipse data
  scan=None  # threshold scan data
  verts=[]   # store box corners
  sky=[]     # used for skybox calculations
  inv=-1     # sky is white, objects black

# look for an read .xml file, if not found, run sky_box

  try: # read xml file with xml_archangel classes
    doc = minidom.parse(filename.split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)
  except:
    pass

  try: # sky and sky sigma values
    xsky=float(elements['sky'][0][1])
    skysig=float(elements['skysig'][0][1])
  except:
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

# set contrast values
  sig=50.
  if '-f' in sys.argv: # if we are doing many files, hold the contrast constant, adjust the sky
    try:
      d=r1-r2
      r2=xsky-0.05*(r1-xsky)
      r1=r2+d
      middle=xsky
    except: # unless, of course, it fucks up
      r1=xsky+sig*skysig
      r2=xsky-0.05*(r1-xsky)
      middle=xsky
  else: # normal files, just calculate it
    if '-c' in sys.argv:
      r2=float(sys.argv[sys.argv.index('-c')+1])
      r1=float(sys.argv[sys.argv.index('-c')+2])
      xsky=r2
      skysig=abs(r2-r1)/10.
    else:
      r1=xsky+sig*skysig
      r2=xsky-0.05*(r1-xsky)
    middle=xsky

# i1,i2,j1,j2,xstep set image edges and zoom
  if '-z' in sys.argv: # if an initial zoom was selected
    if ',' in sys.argv[sys.argv.index('-z')+1]:
      i1=int(sys.argv[sys.argv.index('-z')+1].split(',')[0])
      i2=int(sys.argv[sys.argv.index('-z')+1].split(',')[1])
      j1=int(sys.argv[sys.argv.index('-z')+1].split(',')[2])
      j2=int(sys.argv[sys.argv.index('-z')+1].split(',')[3])
    else:
      try:
        zx=2*int(sys.argv[sys.argv.index('-z')+1])
      except:
        zx=4
      xstep=nx/zx
      i1=nx/2-nx/zx
      i2=nx/2+nx/zx
      j1=ny/2-nx/zx
      j2=ny/2+nx/zx
  else:
    i1=1
    i2=nx
    j1=1
    j2=ny
    xstep=nx/2

  xsig=5.  # skybox sigma
  iwrite=0 # switch if file is modified, if so, will write a .clean version
  lbl=[]   # positions and text for making labels
  marks=[] # points selected for inspection
  igrow=0  # threshold search off
  imarks=0 # mark plotting off
  iap=0    # apertures not defined
  prf_plot=0

  fitsobj=pyfits.open(cont_file,"readonly")
  Z=fitsobj[0].data
  fitsobj.close()
  try: # read xml file with xml_archangel classes
    doc = minidom.parse(cont_file.split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)
    csky=float(elements['sky'][0][1])
    cskysig=float(elements['skysig'][0][1])
  except:
    pass
  r3=csky+3.*cskysig
  r4=csky+50.*cskysig

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

def xytosky(trans,x,y):
  if len(trans) < 7:
    corr=cos(pi*(trans[3]+trans[5]*(y-trans[4]))/180.)
    return trans[0]+(trans[2]/corr)*(x-trans[1]),trans[3]+trans[5]*(y-trans[4]),
  else:
    corr=cos(pi*(trans[4]+trans[6]*(x-trans[1])+trans[7]*(y-trans[5]))/180.)
    return trans[0]+(trans[2]/corr)*(x-trans[1])+(trans[3]/corr)*(y-trans[5]), \
           trans[4]+trans[6]*(x-trans[1])+trans[7]*(y-trans[5])

def skytoxy(trans,ra,dec):
  if len(trans) < 7:
    y=trans[4]+(dec-trans[3])/trans[5]
    corr=cos(pi*(trans[3]+trans[5]*(y-trans[4]))/180.)
    x=trans[1]+(ra-trans[0])*corr/trans[2]
    return x,y
  else:
    c=cos(pi*(trans[4]+trans[6]*(400.-trans[1])+trans[7]*(400.-trans[5]))/180.)
    t1=c*ra/trans[2]-c*trans[0]/trans[2]-trans[3]*dec/(trans[2]*trans[7])
    t1=t1+trans[3]*trans[4]/(trans[2]*trans[7])+trans[1]*(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
    t1=t1/(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
    t2=(dec-trans[4]-trans[6]*(t1-trans[1]))/trans[7]+trans[5]
    c=cos(pi*(trans[4]+trans[6]*(t1-trans[1])+trans[7]*(t2-trans[5]))/180.)
    t1=c*ra/trans[2]-c*trans[0]/trans[2]-trans[3]*dec/(trans[2]*trans[7])
    t1=t1+trans[3]*trans[4]/(trans[2]*trans[7])+trans[1]*(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
    t1=t1/(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
    t2=(dec-trans[4]-trans[6]*(t1-trans[1]))/trans[7]+trans[5]
    return t1,t2

def hms(ra,dec):
  ra=24.*ra/360.
  out='%2.2i' % int(round(ra,4))+'h'
  mn=60.*(ra-int(round(ra,4)))
  out=out+'%2.2i' % int(round(mn,2))+'m'
  sec=60.*(mn-int(round(mn,2)))
  if sec < 10:
    out=out+'0'+'%4.2f' % abs(sec)+'s'
  else:
    out=out+'%5.2f' % abs(sec)+'s'
  if dec < 0:
    sign='-'
  else:
    sign='+'
  dec=abs(dec)
  out=out+sign+'%2.2i' % int(round(dec,4))+'d'
  mn=60.*(dec-int(round(dec,4)))
  out=out+'%2.2i' % int(round(mn,2))+'m'
  sec=60.*(mn-int(round(mn,2)))
  if sec < 10:
    out=out+'0'+'%3.1f' % abs(sec)+'s'
  else:
    out=out+'%4.1f' % abs(sec)+'s'
  return out

def draw_image():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,r3,r4,middle,xsky,skysig,csky,cskysig,sig,filename,nmast,xd,yd,inv,Z,ct
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap
  global ft,cid,channel,markp,pids,geo,last_cmd,cmd,last_peek
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy,rx

  clf() ; ax = fig.add_subplot(111)

# pix will be down one in python coords from normal IRAF coords
# iraf[x,y] = pix[y-1][x-1]
# to plot x,y at center of pixel extent is -0.5

#  palette.set_over('b', 1.0)
#  palette.set_under('g', 1.0)

  zm=ma.masked_where(isnan(pix[j1-1:j2,i1-1:i2]), pix[j1-1:j2,i1-1:i2])
  if '-color' in sys.argv:
    palette=cm.jet
    imshow(-inv*zm,vmin=r2,vmax=r1,extent=(i1-0.5,i2+0.5,j1-0.5,j2+0.5), \
           aspect='equal',origin='lower',interpolation='nearest',cmap=palette)
  else:
    palette=cm.gray
    palette.set_bad('r', 1.0)
    imshow(inv*zm,vmin=-r1,vmax=-r2,extent=(i1-0.5,i2+0.5,j1-0.5,j2+0.5), \
           aspect='equal',origin='lower',interpolation='nearest',cmap=palette)

    palette=cm.jet
    ct=np.arange(r3,r4,(r4-r3)/10.)
#    contour(Z,ct,cmap=palette,extent=(i1,i2,j1,j2))
    contour(Z,ct,cmap=palette,extent=(1,nx,1,ny))

#  imshow(-pix[j1-1:j2,i1-1:i2],vmin=-r1,vmax=-r2,extent=(i1-0.5,i2+0.5,j1-0.5,j2+0.5), \
#         aspect='equal',origin='lower',interpolation='nearest')

  tick=ticks(ax.xaxis.get_majorticklocs()[0],ax.xaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  ax.xaxis.set_minor_locator(minorLocator)
  tick=ticks(ax.yaxis.get_majorticklocs()[0],ax.yaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  ax.yaxis.set_minor_locator(minorLocator)
  if clean == 1:
    suptitle(filename.split('.')[0]+'.clean')
  elif clean == -1:
    suptitle(filename.split('.')[0]+'.fake')
  else:
    suptitle(filename)
  ft=figtext(0.13,0.97,'%.2f' % r3,horizontalalignment='left',verticalalignment='top',color='r')
  ft=figtext(0.90,0.97,'%.2f' % r4,horizontalalignment='right',verticalalignment='top',color='r')
  ft=figtext(0.13,0.93,'%.2f' % r2,horizontalalignment='left',verticalalignment='top',color='b')
  ft=figtext(0.90,0.93,'%.2f' % r1,horizontalalignment='right',verticalalignment='top',color='b')
  if scan: ft=figtext(0.5,0.93,str(len(scan))+' targets',horizontalalignment='center',verticalalignment='top',color='r')
  try:
    strng='%6.0i' % (ix)+' '+'%6.0i' % (iy)
    if abs(pix[iy-1][ix-1]) > 99999.:
      strng=strng+'%11.2e' % pix[iy-1][ix-1]
    else:
      strng=strng+'%11.2f' % pix[iy-1][ix-1]
    try:
      if pssii:
        tmp=map(float,os.popen('DSS_XY '+filename+' '+str(ix)+' '+str(iy)).read().split())
      else:
        tmp=xytosky(trans,ix,iy)
      if 'error' not in tmp:
        strng=strng+'%14.6f' % tmp[0]+'%11.6f' % tmp[1]+'  ('+str(equinox)+')  '
        strng=strng+hms(tmp[0],tmp[1])
    except:
      pass
    ft=figtext(0.50,0.05,strng,horizontalalignment='center',verticalalignment='top',color='k')
  except:
    pass

  x=[] ; y=[]
  for t1,t2 in marks:
    x.append(t1)
    y.append(t2)
  ax.plot(x,y,'r.',markersize=8)
  ax.set_xlim(i1-0.5,i2+0.5)
  ax.set_ylim(j1-0.5,j2+0.5)

  for tmp in lbl:
    text(float(tmp[0]),float(tmp[1]),tmp[2],color='r',horizontalalignment='center',verticalalignment='center',fontsize=14)

  draw()

def clicker(event): # primary event handler
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,r3,r4,middle,xsky,skysig,csky,cskysig,sig,filename,nmast,xd,yd,inv,Z,ct
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap
  global ft,cid,channel,markp,pids,geo,last_cmd,cmd,last_peek
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy,rx

#  if '-f' in sys.argv and event.key not in ['/','up','down']: channel.send(filename)
#  print event.key

  ioff()

  cmd=event.key

  try:
    ix=int(round(event.xdata))
    iy=int(round(event.ydata))
  except:
    ix=0
    iy=0

  if event.key == 'g':  # grab a piece of the frame based on zoom

#    print int(event.xdata)-(i2-i1)/2,event.xdata,(i2-i1)
#    print int(event.ydata)-(j2-j1)/2,event.ydata,(j2-j1)
    out=zeros((j2-j1,i2-i1),'Float32')
    for j in range(j2-j1):
      for i in range(i2-i1):
#        print int(event.xdata)-(i2-i1)/2+i,int(event.xdata)+(i2-i1)/2+i, \
#           int(event.ydata)-(j2-j1)/2+j,int(event.ydata)+(j2-j1)/2+j
        if int(event.xdata)-(i2-i1)/2+i < 0 or \
           int(event.xdata)-(i2-i1)/2+i > nx or \
           int(event.ydata)-(j2-j1)/2+j < 0 or \
           int(event.ydata)-(j2-j1)/2+j > ny:
          out[j][i]=float('nan')
        else:
          try:
            out[j][i]=pix[int(event.ydata)-(j2-j1)/2+j][int(event.xdata)-(i2-i1)/2+i]
          except:
            out[j][i]=float('nan')
    fitsobj2=pyfits.HDUList()
    hdu=pyfits.PrimaryHDU()
    tmp=float(str(hdr.ascardlist()['CRPIX1']).split()[2])
    tmp=tmp-(event.xdata-(i2-i1)/2)
    hdr.update('CRPIX1',tmp)
    tmp=float(str(hdr.ascardlist()['CRPIX2']).split()[2])
    tmp=tmp-(event.ydata-(j2-j1)/2)
    hdr.update('CRPIX2',tmp)
    hdu.header=hdr
    hdu.data=out
    fitsobj2.append(hdu)
    prefix=filename.split('.')[0]
    if os.path.isfile(prefix+'.fits'):
      if os.path.isfile(prefix+'.grab'): os.remove(prefix+'.grab')
      fitsobj2.writeto(prefix+'.grab')
    else:
      fitsobj2.writeto(prefix+'.fits')
    fitsobj2.close()

  if event.key in ['/','up','down']:
    disconnect(cid)
    close()
    if pids:
      pids=kill_pids(pids,0)
    time.sleep(0.5) # gluge to catch '/' before it passes it to nearest xwindow
    sys.exit()

  elif event.key == 'G':
    fitsobj2=pyfits.HDUList()
    hdu=pyfits.PrimaryHDU()
    hdu.header=hdr
    hdu.data=pix[j1-1:j2,i1-1:i2]
    fitsobj2.append(hdu)
    fitsobj2.writeto(filename.split('.')[0]+'.snap')
    fitsobj2.close()

  elif event.key in [None,'control','alt','right','left','escape']:
    pass

  elif event.xdata == None or event.ydata == None:
    pass

  elif event.key in ['L']:
    fig.savefig(filename.split('.')[0]+'_snap.pdf')
    print 'output to',filename.split('.')[0]+'_snap.pdf'

  elif event.key == 'm':
    line='0 1\ncontrast: values\n7 20\nbottom '+str(r2)+'\nmiddle '+str(middle)+'\ntop '+str(r1)+'\n'
    p = subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -entry_field -noadd', \
                         shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=p.communicate(line)[0]
    if '>>>aborting<<<' not in tmp:
      r1=float(tmp.split('\n')[2])
      middle=float(tmp.split('\n')[1])
      r2=float(tmp.split('\n')[0])
      if middle == 0.: middle=(r1-r2)/2.

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

  elif event.key == 'C':
    rold=r4
    k=0.5-(event.ydata-i1)/(i2-i1)
    r3=r3+3.*k*cskysig
    k=0.5-(event.xdata-i1)/(i2-i1)
    r4=r4+k*(r4-r3)

  elif event.key == 'c':
    rold=r1
    k=0.5+(event.xdata-i1)/(i2-i1)
    r1=r1*k
    if r1 < middle: r1=(rold-middle)/2.+middle
    r2=middle-0.05*(r1-middle)

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
        i1=int(nx-2*xstep)
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
#  draw()
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
fig = figure(figsize=(fig_size, fig_size), dpi=80)
ax = fig.add_subplot(111)
try:
  manager = get_current_fig_manager()
  manager.window.title('')
  manager.window.geometry(geo['main_window'])
except:
  pass

nmast=0
pids=[]
cmd=None ; last_cmd=None

filename=sys.argv[-2]
if '.' not in filename: filename=filename.replace('.','')+'.fits'
cont_file=sys.argv[-1]
if '.' not in cont_file: cont_file=cont_file.replace('.','')+'.fits'

gray()
get_data()
if '-L' in sys.argv:
  fig_size=int(geo['main_size'])
  fig = figure(figsize=(fig_size, fig_size), dpi=80)
  draw_image()
#  draw()
  fig.savefig(filename.split('.')[0]+'_snap.pdf')
  sys.exit()
else:
  draw_image()

cid=connect('key_press_event',clicker)
show()
