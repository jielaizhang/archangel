#!/usr/bin/env python

import pyfits,sys,os,time,subprocess,signal
from math import *
from xml_archangel import *
from pylab import *
from matplotlib.ticker import MultipleLocator # needed to fix up minor ticks
from matplotlib.patches import Ellipse, Polygon

# quick display program ala prf_edit, enter a list of files or -f image
# first look for profile.py routine, aborts or output new options

def find_imin(xdata,ydata):
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap,rstop
  rmin=1.e33
  if prf_plot >= 1:
    for line in prf:
      th=90.-180.*atan((xdata-line[14])/(ydata-line[15]))/pi
      rtest=((xdata-line[14])**2+(ydata-line[15])**2)**0.5
      rr=findr(th*pi/180.,1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])
      if abs(rtest-rr) < rmin:
        rmin=abs(rtest-rr)
        imin=prf.index(line)
  else:
    for line in scan:
      rtest=((xdata-line[0])**2+(ydata-line[1])**2)**0.5
      if rtest < rmin:
        rmin=rtest
        imin=scan.index(line)

  return imin

def threshold(k):
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,inv
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap,rstop
  prf_plot=0
  marks=[]
  sig=sig*k
  line=prf[igrow]
#  print xsky,sig,skysig
  for i in range(int(line[14]-line[3]-5),int(line[14]+line[3]+5)):
    for j in range(int(line[15]-line[3]-5),int(line[15]+line[3]+5)):
      th=90.-180.*atan((i+1-line[14])/(j+1-line[15]))/pi
      rtest=((i+1-line[14])**2+(j+1-line[15])**2)**0.5
      rr=findr(th*pi/180.,1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])
      if (i+1,j+1) not in marks and rtest < rr:
#      if pix[j][i] > xsky+sig*skysig and rtest < rr:
        intens=ifilter(i,j)
        if intens > xsky+sig*skysig:
          for ii in [i-1,i,i+1]:
            for jj in [j-1,j,j+1]:
              if (ii+1,jj+1) not in marks and \
                pix[jj][ii] == pix[jj][ii]: marks.append((ii+1,jj+1))
  out=open('s.tmp','w')
  for x,y in marks:
    print >> out,x,y
  out.close()

def ifilter(i,j):
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,inv
  return 0.80*pix[j][i]+(0.15/4.)*(pix[j-1][i]+pix[j+1][i]+pix[j][i-1]+pix[j][i+1])+ \
         (0.05/4.)*(pix[j-1][i-1]+pix[j-1][i+1]+pix[j+1][i-1]+pix[j+1][i+1])

def find_mag():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,inv
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap,rstop
  tmp=0.
  for i,j in marks:
   if pix[i-1][j-1] == pix[i-1][j-1]: tmp=tmp+pix[i-1][j-1]-xsky
  return -2.5*log10(tmp)

def help():
  return '''
Usage: qphot option master_file

quick grayscale display GUI for quick photometry

cursor commands:

/ = abort/move to next image      q = quit
z = zoom                          Z = recenter
r = unzoom                        R = reset zoom                    
y = use cleaned file (.clean)     f = use fake file (.fake)

c = contrast                      m = manual contrast values
v = invert grayscale              G = make snap of current image
L = make hardcopy of current frame

p = peek at values                . = mark position/list coords
w = update xml file               , = clear marks
j = mark a coord file (s.tmp)     ? = help window

i = plot scan data (s.tmp)        I = do scan

h = do circle photometry          H = grow aperture
  = select/shrink circle          J = shrink aperture

a,1-9 = delete circle             b = delete box'''

#  subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -text_window -f probe_data.tmp &',shell=True)

def get_data():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,inv
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap,rstop
  global ft,cid,channel,markp,pids,geo,last_cmd,cmd,last_peek
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy,rx

  if '-y' in sys.argv:           # switch to use clean datafile
    clean=1
    fitsobj=pyfits.open(filename.split('.')[0]+'.clean',"readonly")
  else:
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
  prf_plot=0

# look for an read .xml file, if not found, run sky_box

  try: # read xml file with xml_archangel classes
    doc = minidom.parse(filename.split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    for t in elements['array']:
      if t[0]['name'] == 'prf': # ellipse data
        prf=[]
        head=[]
        pts=[]
        for z in t[2]['axis']:
          head.append(z[0]['name'])
          pts.append(map(float,z[1].split('\n')))
        for z in range(len(pts[0])):
          tmp=[]
          for w in head:
            tmp.append(pts[head.index(w)][z])
# don't do this, causes small nummercal errors in iso_prf
#          if tmp[13] >= 270: tmp[13]=tmp[13]-360.
#          if tmp[13] > 90: tmp[13]=tmp[13]-180.
#          if tmp[13] <= -270: tmp[13]=tmp[13]+360.
#          if tmp[13] < -90: tmp[13]=tmp[13]+180.
          prf.append(tmp)

  except:
    pass

  if '-c' not in sys.argv:
    try: # sky and sky sigma values
      xsky=float(elements['sky'][0][1])
      skysig=float(elements['skysig'][0][1])
    except: # if no sky, get a 1st guess
      if nx < 50:
        go_cmd='sky_box -s '+filename
      else:
        go_cmd='sky_box -f '+filename
      try: # gludge for SQIID data, don't do the edge
        if 'SQIID' in hdr['INSTRUME']: go_cmd='sky_box -c '+filename+' 100 400 100 400'
      except:
        pass
      tmp=os.popen(go_cmd).read()
      if len(tmp) < 1 or 'error' in tmp: # try a full sky search
        go_cmd='sky_box -s '+filename
        tmp=os.popen(go_cmd).read()
        if len(tmp) < 1 or 'error' in tmp:
          print 'error in figuring out sky, aborting'
          sys.exit()
      xsky=float(tmp.split()[2])
      skysig=float(tmp.split()[3])

# sky_boxes if they exist

  try:
    for t in elements['array']:
      if t[0]['name'] == 'sky_boxes': # sky_box data
        head=[]
        pts=[]
        for z in t[2]['axis']:
          head.append(z[0]['name'])
          pts.append(map(float,z[1].split('\n')))
        for z in range(len(pts[0])):
          tmp=[]
          for w in head:
            tmp.append(pts[head.index(w)][z])
          data=[]
          for i in range(int(tmp[0])-10,int(tmp[0])+10,1):
            for j in range(int(tmp[1])-10,int(tmp[1])+10,1):
              try:
                data.append(pix[j][i])
              except:
                pass
          t=xits(data,3.)
          if str(sum(data)) != 'nan':
            sky.append((t[2],t[3],t[4],t[5],int(tmp[0]),int(tmp[1]),20,sum(data)))
  except:
    pass

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

def ellipse(axis,x,r,s,xc,yc,th):

# routine to solve coeffients of elliptical equation
# of form Ax^2 + By^2 + Cx + Dy + Exy + F = 0
# r = major axis, s = minor axis

  m=cos(th)
  n=sin(th)
  xo=0.
  yo=0.
  a=(s**2)*(m**2)+(r**2)*(n**2)
  b=(s**2)*(n**2)+(r**2)*(m**2)
  c=-2.*((s**2)*m*xo+(r**2)*n*yo)
  d=-2.*((s**2)*n*xo+(r**2)*m*yo)
  e=2.*((s**2)*m*n-(r**2)*m*n)
  f=(s**2)*(xo**2)+(r**2)*(yo**2)-(r**2)*(s**2)

# for given x value, find two y values on ellipse
  if axis == 'x':
    x=x-xc
    t1=(d+e*x)
    t2=t1**2
    t3=4.*b*(a*(x**2)+c*x+f)
    t4=2.*b
    try:
      return yc+(-t1+(t2-t3)**0.5)/t4,yc+(-t1-(t2-t3)**0.5)/t4
    except:
      return 'nan','nan'
# for given y value, find two x values on ellipse
  else:
    x=x-yc
    t1=(c+e*x)
    t2=t1**2
    t3=4.*a*(b*(x**2)+d*x+f)
    t4=2.*a
    try:
      return xc+(-t1+(t2-t3)**0.5)/t4,xc+(-t1-(t2-t3)**0.5)/t4
    except:
      return 'nan','nan'

def piece(vert):
  det=0.
  for i in range(len(vert)):
    j=i+1
    if j >= len(vert): j=0
    det=det+(vert[i][0]*vert[j][1]-vert[j][0]*vert[i][1])
  return abs(det/2.)

def findr(t,eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  c1=bsq*(cos(t))**2+asq*(sin(t))**2
  c2=(asq-bsq)*2*sin(t)*cos(t)
  c3=bsq*(sin(t))**2+asq*(cos(t))**2
  c4=asq*bsq
  return (c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**0.5

def inside(x,y,eps,a,d,xc,yc):
  edge=[]
  for i in [x-0.5,x+0.5]:
    for j in [y-0.5,y+0.5]:
      if i-xc == 0:
        t=pi/2.
      else:
        t=atan((j-yc)/(i-xc))
      if ((i-xc)**2+(j-yc)**2)**0.5 < findr(t,eps,a,d,xc,yc):
        edge.append((i,j))
  return edge

def xits(xx,xsig):
  xmean1=0. ; sig1=0.
  for t in xx:
    xmean1=xmean1+t
  try:
    xmean1=xmean1/len(xx)
  except:
    return 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'
  for t in xx:
    sig1=sig1+(t-xmean1)**2
  try:
    sig1=(sig1/(len(xx)-1))**0.5
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
    for t in xx:
      if abs(t-xold) < xsig*sig2:
        npts+=1
        dum=dum+t
    try:
      xmean2=dum/npts
    except:
      return xmean1,sig1,'NaN','NaN',len(xx),'NaN','NaN'
    dum=0.
    for t in xx:
      if abs(t-xold) < xsig*sig2:
        dum=dum+(t-xmean2)**2
    try:
      sig2=(dum/(npts-1))**0.5
      if sig2 == 0.: return xmean1,sig1,xmean2,sig2,len(xx),npts,its
    except:
      return xmean1,sig1,'NaN','NaN',len(xx),'NaN','NaN'
  return xmean1,sig1,xmean2,sig2,len(xx),npts,its

def eapert(xc,yc,eps,th,xsky,rr):

  data=[]
  old_area=0.

  left=max(0,int(xc-rr-5))
  right=min(int(xc+rr+5),nx)
  bottom=max(0,int(yc-rr-5))
  top=min(int(yc+rr+5),ny)

  sum=0. ; sum2=0.
  tsum=0.
  npts=0.
  tot_npts=0.
  new_sky=[]

  if xsky == 0.:
    for x in arange(left,right,1):
      for y in arange(bottom,top,1):
        tmp=inside(x,y,1.,rr,0.,xc,yc)
        tmp2=inside(x,y,1.,rr+5.,0.,xc,yc)

        if not tmp and tmp2 and str(pix[y-1][x-1]) != 'nan':
          new_sky.append(pix[y-1][x-1])

    return xits(new_sky,2.5)[2]

  for x in arange(left,right,1):
    for y in arange(bottom,top,1):
      area=0.
      tmp=inside(x,y,eps,rr,-th*pi/180.,xc,yc)

      vert=[]
      if tmp and len(tmp) < 4:
        y1,y2=ellipse('x',x-0.5,rr,rr*eps,xc,yc,th)
        if str(y1) != 'nan' and str(y2) != 'nan':
          if ((y-y1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x-0.5,y1))
          if ((y-y2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x-0.5,y2))
        y1,y2=ellipse('x',x+0.5,rr,rr*eps,xc,yc,th)
        if str(y1) != 'nan' and str(y2) != 'nan':
          if ((y-y1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x+0.5,y1))
          if ((y-y2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x+0.5,y2))
        x1,x2=ellipse('y',y-0.5,rr,rr*eps,xc,yc,th)
        if str(x1) != 'nan' and str(x2) != 'nan':
          if ((x-x1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x1,y-0.5))
          if ((x-x2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x2,y-0.5))
        x1,x2=ellipse('y',y+0.5,rr,rr*eps,xc,yc,th)
        if str(x1) != 'nan' and str(x2) != 'nan':
          if ((x-x1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x1,y+0.5))
          if ((x-x2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x2,y+0.5))

        if vert:
          x0=vert[-1][0]
          y0=vert[-1][1]
          for i in range(len(tmp)):
            dmin=1.e33
            for r,s in tmp:
              dd=((x0-r)**2+(y0-s)**2)**0.5
              if dd < dmin:
                t=(r,s)
                dmin=dd
            try:
              x0=t[0]
              y0=t[1]
              vert.append(t)
              tmp.remove(t)
            except:
              pass
          area=piece(vert)
      elif len(tmp) == 4:
        area=1.

#      if area > 0.: out.write(str(x)+' '+str(y)+' '+str(pix[y-1][x-1])+' '+str(area)+'\n')

      if str(pix[y-1][x-1]) != 'nan':
        sum=sum+area*(pix[y-1][x-1]-xsky)
        tsum=tsum+area*pix[y-1][x-1]
        npts=npts+area
      tot_npts=tot_npts+area

#  print '%16.8e' % rr,
#  print '%16.8e' % (-2.5*log10(sum)),
#  print '%16.8e' % sum,
#  print '%16.8e' % npts,
#  print '%16.8e' % tsum,
#  print '%16.8e' % xsky
  return -2.5*log10(sum)

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

def eplot(prf):
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,inv
  global ft,cid,channel,markp,pids,geo,last_cmd,cmd,last_peek
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy,rx

  ells=[Ellipse((l[0],l[1]),2.*(l[2]/(math.pi*(1.-l[3])))**0.5, \
                  2.*(1.-l[3])*((l[2]/(math.pi*(1.-l[3])))**0.5),l[4],fill=0) for l in prf]
  n=0
  for e,l in zip(ells,prf):
    n=n+1
    if prf_plot == 2 and n != last_peek+1: continue
    e.set_clip_box(ax.bbox)
    e.set_alpha(1.0)
    if n == 1:
      e.set_edgecolor('r')
    else:
      e.set_edgecolor('b')
    ax.add_artist(e)
    if prf_plot == 2:
      ax.plot([l[14]-(l[3]+5.)*cos(l[13]*pi/180.),l[14]+(l[3]+5.)*cos(l[13]*pi/180.)], \
              [l[15]-(l[3]+5.)*sin(l[13]*pi/180.),l[15]+(l[3]+5.)*sin(l[13]*pi/180.)],'r')
      bt=l[3]*(1.-l[12]) ; dt=((l[13]+90.)*pi/180.)
      ax.plot([l[14]-(bt+5.)*cos(dt),l[14]+(bt+5.)*cos(dt)], \
              [l[15]-(bt+5.)*sin(dt),l[15]+(bt+5.)*sin(dt)],'r')
  ax.set_xlim(i1-0.5,i2+0.5)
  ax.set_ylim(j1-0.5,j2+0.5)

def draw_image():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,inv
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap,rstop
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
  ft=figtext(0.13,0.93,'%.2f' % r2,horizontalalignment='left',verticalalignment='top',color='b')
  ft=figtext(0.90,0.93,'%.2f' % r1,horizontalalignment='right',verticalalignment='top',color='b')
  if igrow:
    ft=figtext(0.33,0.91,'%.1f' % xsky,horizontalalignment='left',verticalalignment='top',color='g')
    if len(marks): ft=figtext(0.50,0.91,'%.3f' % find_mag(),horizontalalignment='left',verticalalignment='top',color='g')
    ft=figtext(0.70,0.91,'%.1f' % (sig*skysig),horizontalalignment='right',verticalalignment='top',color='g')
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

  if prf_plot >= 1:
    eplot(prf)
  elif prf_plot == -1:
    eplot(scan)

  for tmp in lbl:
    text(float(tmp[0]),float(tmp[1]),tmp[2],color='r',horizontalalignment='center',verticalalignment='center',fontsize=14)

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
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,inv
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap,rstop
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

  if event.key in ['/','up','down']:
    disconnect(cid)
    close()
    if pids:
      pids=kill_pids(pids,0)
    time.sleep(0.5) # gluge to catch '/' before it passes it to nearest xwindow
    if '-v' in sys.argv: print 'clean exit',event.xdata,event.ydata
    sys.exit()

  elif event.key == 'q':
    disconnect(cid)
    close()
    if pids: pids=kill_pids(pids,1)
    time.sleep(0.5)
    if '-f' not in sys.argv: print 'aborting',event.xdata,event.ydata
    sys.exit()

  elif event.key in [None,'control','alt','right','left','escape']:
    pass

  elif event.xdata == None or event.ydata == None:
    pass

  elif event.key in ['a','2','3','4','5','6','7','8','9','b']:
    if not igrow and not imarks: iwrite=1
    if event.key not in ['a','b']:
      r=float(event.key)
      xd=event.xdata
      yd=event.ydata
    else:
      if event.key == 'a':
        try:
          r=((event.xdata-xd)**2.+(event.ydata-yd)**2.)**0.5
        except:
          xd=event.xdata
          yd=event.ydata
      if event.key == 'b':
        try:
          for j in range(int(yd),int(event.ydata)):
            for i in range(int(xd),int(event.xdata)):
              pix[j][i]=float('nan')
          del r,xd,yd
        except:
          xd=event.xdata
          yd=event.ydata
    try:
      for j in range(max(int(yd-r-2),0),min(int(yd+r+2),ny)):
        for i in range(max(int(xd-r-2),0),min(int(xd+r+2),nx)):
          rr=((i+1-xd)**2+(j+1-yd)**2)**0.5
          if rr < r:
            if imarks or igrow:
              if (i+1,j+1) not in marks: marks.append((i+1,j+1))
            else:
              pix[j][i]=float('nan')
      del r,xd,yd
    except:
      pass
    if igrow or imarks: dump_marks()

  elif event.key in ['h','H','J','d']:
    if event.key == 'h':
      iap=1
      prf_plot=-1
      if 'HST' in hdr['TELESCOP']:
        rstop=50.
      else:
        rstop=10.
      tmp=os.popen('gasp_images -f '+filename+' '+str(xsky)+' '+str(50.*skysig)+' 5 true').read()
#      print 'gasp_images -f '+filename+' '+str(xsky)+' '+str(3.*skysig+xsky)+' 5 true'
      rmin=1.e33
#      print len(tmp.split('\n'))
      for line in tmp.split('\n')[:-1]:
        z=line.split()
#        print z,((float(z[0])-event.xdata)**2.+(float(z[1])-event.ydata)**2.)**0.5
        if ((float(z[0])-event.xdata)**2.+(float(z[1])-event.ydata)**2.)**0.5 < rmin:
          rmin=((float(z[0])-event.xdata)**2.+(float(z[1])-event.ydata)**2.)**0.5
          scan=[[float(z[0]),float(z[1]),pi*rstop**2.,0.,0.,0.]]
          scan.append([float(z[0]),float(z[1]),pi*(rstop+5.)**2.,0.,0.,0.])
          scan.append([float(z[0]),float(z[1]),pi*(rstop+10.)**2.,0.,0.,0.])

      print 'found',scan[0],'%.1f' % event.xdata,'%.1f' % event.ydata,'%.2f' % rmin

    elif event.key == 'H':
      rstop=rstop+2.
      xd=scan[0][0] ; yd=scan[0][1]
      scan=[[xd,yd,pi*rstop**2.,0.,0.,0.]]
      scan.append([xd,yd,pi*(rstop+5.)**2.,0.,0.,0.])
      scan.append([xd,yd,pi*(rstop+10.)**2.,0.,0.,0.])

    elif event.key == 'J':
      rstop=rstop-2.
      xd=scan[0][0] ; yd=scan[0][1]
      scan=[[xd,yd,pi*rstop**2.,0.,0.,0.]]
      scan.append([xd,yd,pi*(rstop+5.)**2.,0.,0.,0.])
      scan.append([xd,yd,pi*(rstop+10.)**2.,0.,0.,0.])

    elif event.key in ['d','h']:
      tsky=(eapert(scan[0][0],scan[0][1],1.,0.,0.,rstop+5.))
      out=open('apertures.tmp','w')
      for rr in arange(2.,rstop,(rstop-2.)/20.):
        out.write('%.2f' % rr)
        dum=(eapert(scan[0][0],scan[0][1],1.,0.,tsky,rr))
        out.write(' '+str(dum)+' '+str(scan[0][0])+' '+str(scan[0][1])+'\n')
        print '%.1f %.2f %.2f' % (rr,dum,tsky)
      out.close()

  elif event.key == '?':
    fout=open('probe_data.tmp','w')
    fout.write(help()+'\n')
    fout.close()
    subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -text_window -x -f probe_data.tmp &',shell=True)

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

  elif event.key == 'v':
    inv=-inv

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

    if prf_plot:
      imin=find_imin(event.xdata,event.ydata)
      if event.key != last_cmd:
        fout=open(file,'w')
        fout.write('8\n')
        print >> fout,''
        print >> fout,' INTEN    RAD   ITER   NUM     ECC POSANG    X0     Y0'
        print >> fout,''
      else:
        fout=open(file,'a')
      for i in [0,3,6,7,12,13,14,15]:
        print >> fout,'%6.1f' % (prf[imin][i]),
      print >> fout,' '
      fout.close()

    else:
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
#      p=subprocess.Popen('/usr/local/bin/rxvt -fn 6x13 -bg black -fg magenta +sb -cr black -T "DN Values"'+ \
#                         ' -geometry 80x13'+geo['peek_window']+' -e '+os.environ['ARCHANGEL_HOME']+'/util/monitor.py '+ \
#                         file+' &',shell=True)
      p=subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/tterm.py -f magenta -r 13 -c 80 '+ \
        '-p '+geo['peek_window']+' '+os.environ['ARCHANGEL_HOME']+'/util/monitor.py '+file,shell=True)
      pids.append([p.pid+2,1,file])

    if event.key != last_cmd:
      p=subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/tterm.py -f red -r 25 -c 80 '+ \
        '-p '+geo['sky_window']+' '+os.environ['ARCHANGEL_HOME']+'/util/monitor.py '+file,shell=True)
      pids.append([p.pid+2,1,file])
#      p=subprocess.Popen('/usr/local/bin/rxvt -fn 6x13 -bg black -fg red +sb -cr black -T "Sky Measurements"'+ \
#                         ' -geometry 75x26'+geo['sky_window']+' -e '+os.environ['ARCHANGEL_HOME']+'/util/monitor.py '+ \
#                         file+' &',shell=True)
#      pids.append([p.pid+1,1,file])

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

import warnings
warnings.filterwarnings('ignore')

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

if '-f' in sys.argv:
  master=[tmp[:-1] for tmp in open(sys.argv[-1],'r').readlines()]
  filename=master[0]
  max_width=0
  file=str(int(time.time()))+'_files.tmp'
  fout=open(file,'w')
  max_length=min(len(master)+1,150)
  fout.write(str(max_length)+'\nno header\n')
  for z in master:
    if len(z) > max_width: max_width=len(z)
    if z == filename:
      fout.write('>> '+z+'\n')
    else:
      fout.write('   '+z+'\n')
  fout.close()
  p=subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/tterm.py -f green -r '+str(max_length)+ \
    ' -c '+str(max_width+10)+ \
    ' -p '+geo['listbox']+' '+os.environ['ARCHANGEL_HOME']+'/util/monitor.py '+file,shell=True)
  pids.append([p.pid+2,0,file])
#  p=subprocess.Popen('/usr/local/bin/rxvt -fn 6x13 -bg black -fg green +sb -cr black -T "Files" '+ \
#                     ' -geometry '+str(max_width+10)+'x'+str(max_length)+geo['listbox']+' -e '+ \
#                     os.environ['ARCHANGEL_HOME']+'/util/monitor.py '+file+' &',shell=True)
#  pids.append([p.pid+1,0,file])

#  import socket
#  p=subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets_socket.py -listbox -f '+sys.argv[-1]+' &',shell=True)
#  time.sleep(1)
#  channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#  channel.connect(('localhost',2727))
#  channel.send(filename)

else:
  filename=sys.argv[-1]
  if '.' not in filename or sys.argv[-1][-1] == '.': filename=filename.replace('.','')+'.fits'

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

if '-s' in sys.argv:
  for t in sky:
    v=[(t[4]-10,t[5]-10),(t[4]+10,t[5]-10),(t[4]+10,t[5]+10),(t[4]-10,t[5]+10),(t[4]-10,t[5]-10)]
    poly=Polygon(v, fill=0, edgecolor='b')
    ax.add_patch(poly)

cid=connect('key_press_event',clicker)
show()
