#!/usr/bin/env python

import pyfits,sys,os,time,subprocess,signal
from math import *
from xml_archangel import *
from pylab import *
from matplotlib.ticker import MultipleLocator # needed to fix up minor ticks
from matplotlib.patches import Ellipse, Polygon

# quick display program ala prf_edit, enter a list of files or -f image
# first look for profile.py routine, aborts or output new options

def point_inside_polygon(x,y,polly):
  n = len(polly)
  inside = False
  p1x,p1y = polly[0]
  for i in range(n+1):
    p2x,p2y = polly[i % n]
    if y > min(p1y,p2y):
      if y <= max(p1y,p2y):
        if x <= max(p1x,p2x):
          if p1y != p2y:
            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
          if p1x == p2x or x <= xinters:
            inside = not inside
    p1x,p1y = p2x,p2y
  return inside

def find_imin(xdata,ydata):
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap
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
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,polly,inv
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap
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
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,polly,inv
  return 0.80*pix[j][i]+(0.15/4.)*(pix[j-1][i]+pix[j+1][i]+pix[j][i-1]+pix[j][i+1])+ \
         (0.05/4.)*(pix[j-1][i-1]+pix[j-1][i+1]+pix[j+1][i-1]+pix[j+1][i+1])

def find_mag():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,polly,inv
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap
  tmp=0.
  for i,j in marks:
   if pix[i-1][j-1] == pix[i-1][j-1]: tmp=tmp+pix[i-1][j-1]-xsky
  return -2.5*log10(tmp)

def smash_ellipses(imin):
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky

  try:
    for n in range(imin+1,len(prf)): 
      for i in [12,13,14,15]:
        prf[n][i]=prf[imin][i]
      prf[n][6]=0.

  except:
    pass

def clean_ellipses():
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap

  try:
    for n in range(len(prf)-1): 
      if prf[n][6] == -99:           # if iteration counter zero, clean
        ibot=0
        for i in range(n,0,-1):
          if prf[i][6] != -99:
            ibot=i
            break
        itop=len(prf)
        for i in range(n,len(prf)):
          if prf[i][6] != -99:
            itop=i
            break
        if ibot == 0:
          for i in range(12,15): prf[n][i]=prf[itop][i]
        elif itop >= len(prf):
          for i in range(12,15): prf[n][i]=prf[ibot][i]
        else:

# linear interp for ellipse parameters of cross-over isophote

          k=(prf[n][3]-prf[ibot][3])/(prf[itop][3]-prf[ibot][3])
          xtop=prf[itop][13]
          xbot=prf[ibot][13]
          if xbot <= xtop:
            if xtop-xbot > 90:
#            xang=((xtop-180.)+xbot)/2.
              xang=((xtop-180.)-xbot)*k+xbot
            else:
#            xang=(xtop+xbot)/2.
              xang=(xtop-xbot)*k+xbot
          else:
            if xbot-xtop > 90:
              xang=((xbot-180.)+xtop)/2.
            else:
              xang=(xbot+xtop)/2.
          prf[n][13]=xang
          for i in [12,14,15]:
            prf[n][i]=(prf[itop][i]-prf[ibot][i])*k+prf[ibot][i]
        prf[n][6]=0.

  except:
    pass

def help():
  return '''
Usage: probe option master_file

quick grayscale display GUI

options: -f = do file of images
         -v = output exit coords
         -t = plot ellipses at start
         -i = plot scan data at start (from s.tmp)
         -m = plot marks (x&y from marks.tmp)
         -s = plot marks (RA&Dec from marks.tmp)
         -c = contrast values r1 & r2
     -color = run with jet colormap
       -win = change default window (size+xw+yw)
       -z N = start with zoom factor N (default=2)
              or i1,i2,i3,i4 for pixel corners

cursor commands:

/ = abort/move to next image      q = quit
z = zoom                          Z = recenter
r = unzoom                        R = reset zoom                    
y = use cleaned file (.clean)     f = use fake file (.fake)

c = contrast                      m = manual contrast values
v = invert grayscale              G = make snap of current image
L = make hardcopy of current frame

s = sky boxes                     e = plot labels
\ = mark photometry points        ; = threshold grow search

p = peek at values                . = mark position/list coords
w = update xml file               , = clear marks
j = mark a coord file (s.tmp)     ? = help window

i = plot scan data (s.tmp)        I = do scan

t = toggle ellipse plot           u = inspect ind ellipses
x = mark isophote for cleaning    o = clean ellipses
X = delete the ellipse            k = smash outer ellipses

h = do circle photometry          H = grow circle
  = select/shrink circle          J = delete aperture

a,1-9 = delete circle             b = delete box'''

#  subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -text_window -f probe_data.tmp &',shell=True)

def get_data():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,polly,inv
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap
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
      skysig=float(tmp.split()[3])/5.

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

  if '-t' in sys.argv and prf:
    prf_plot=1
  else:
    prf_plot=0

  if '-m' in sys.argv or '-s' in sys.argv:
    try:
      tmp=[(map(float, tmp.split())) for tmp in open('marks.tmp','r').readlines()]
      marks=[] ; imarks=1
      for z in tmp:
        if '-s' in sys.argv: 
          marks.append((skytoxy(trans,z[0],z[1])[0],skytoxy(trans,z[0],z[1])[1]))
        else:
          marks.append((z[0],z[1]))
    except:
      try:
        for t in elements['array']:
          if t[0]['name'] == 'marks': # ellipse data
            marks=[]
            head=[]
            pts=[]
            for z in t[2]['axis']:
              head.append(z[0]['name'])
              pts.append(map(float,z[1].split('\n')))
            for z in range(len(pts[0])):
              tmp=[]
              for w in head:
                tmp.append(pts[head.index(w)][z])
              marks.append(tmp)
      except:
        pass

  if '-i' in sys.argv:
    try:
      scan=[(map(float, tmp.split())) for tmp in open('s.tmp','r').readlines()]
      def determine(t):
        if t[2] < 1. or t[3] > 0.999: return False
        return True
      scan[:] = [t for t in scan if determine(t)]
      prf_plot=-1
    except:
      pass

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

  if xsky == 'None':
    for x in arange(left,right,1):
      for y in arange(bottom,top,1):
        tmp=inside(x,y,eps,rr,-th*pi/180.,xc,yc)
        if not tmp and str(pix[y-1][x-1]) != 'nan': new_sky.append(pix[y-1][x-1])
    xsky=xits(new_sky,2.5)[2]

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
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,polly,inv
  global ft,cid,channel,markp,pids,geo,last_cmd,cmd,last_peek
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy,rx

  if len(prf[0]) > 7:
    ells=[Ellipse((l[14],l[15]),2.*l[3],2.*l[3]*(1.-l[12]),l[13],fill=0) for l in prf]
  else:
#    for l in prf:
#      print l[0],l[1],2.*(l[2]/(math.pi*(1.-l[3])))**0.5, \
#            2.*(1.-l[3])*((l[2]/(math.pi*(1.-l[3])))**0.5),l[4]
    ells=[Ellipse((l[0],l[1]),2.*(l[2]/(math.pi*(1.-l[3])))**0.5, \
                  2.*(1.-l[3])*((l[2]/(math.pi*(1.-l[3])))**0.5),l[4],fill=0) for l in prf]
  n=0
  for e,l in zip(ells,prf):
    n=n+1
    if prf_plot == 2 and n != last_peek+1: continue
    e.set_clip_box(ax.bbox)
    e.set_alpha(1.0)
    try:
      if l[6] == 0:          # no iterations or cleaned
        e.set_edgecolor('g')
      elif l[6] == -99:      # to be cleaned
        e.set_edgecolor('c')
      elif l[6] == -1:       # iteration failed, used last ellipse
        e.set_edgecolor('r')
      else:                  # good fit
        e.set_edgecolor('b')
    except:
      e.set_edgecolor('r')
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
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,polly,inv
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
  if scan: ft=figtext(0.5,0.93,str(len(scan))+' targets',horizontalalignment='center',verticalalignment='top',color='r')
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
  ax.plot(x,y,'m.',markersize=8)
  ax.set_xlim(i1-0.5,i2+0.5)
  ax.set_ylim(j1-0.5,j2+0.5)

  try:
    zlast=polly[0]
    for z in polly[1:]:
      ax.plot([zlast[0],z[0]],[zlast[1],z[1]],color='r')
      zlast=z
  except:
    pass

  if prf_plot >= 1:
    eplot(prf)
  elif prf_plot == -1:
    eplot(scan)

  for tmp in lbl:
    text(float(tmp[0]),float(tmp[1]),tmp[2],color='r',horizontalalignment='center',verticalalignment='center',fontsize=14)

  draw()

def update_xml():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,polly,inv
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap
  global ft,cid,channel,markp,pids,geo,last_cmd,cmd,last_peek
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy,rx

#  if filename.split('.')[-1] not in ['fits','clean','boxcar','fake','stars']: return  # dont update non-data files

#  try:
#    line='INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n'
#    for z in prf:
#      for t in z:
#        line=line+'%16.8e' % (t)+' '
#      line=line+'\n'
#    p=subprocess.Popen('xml_archangel -a '+filename.split('.')[0]+'.xml prf', \
#                       shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
#    p.communicate(line)
#    try:
#      tmp=os.waitpid(p.pid,0)
#    except:
#      pass
#  except:
#    pass

  try:
    if sky and '-c' not in sys.argv:
      if not os.path.isfile(filename.split('.')[0]+'.xml'): # create an xml file if none found
        os.system('xml_archangel -c '+filename.split('.')[0]+' archangel')

      p=subprocess.Popen('xml_archangel -e '+filename.split('.')[0]+' sky units=\'DN\' '+str(xsky),shell=True)
      tmp=os.waitpid(p.pid,0)
      p=subprocess.Popen('xml_archangel -e '+filename.split('.')[0]+' skysig units=\'DN\' '+str(skysig),shell=True)
      tmp=os.waitpid(p.pid,0)

      p=subprocess.Popen('xml_archangel -a '+filename.split('.')[0]+' sky_boxes', \
                          shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
      lines='x y box_size\n'
      for z in sky:
        lines=lines+str(z[-4])+' '+str(z[-3])+' '+str(z[-2])+'\n'
      p.communicate(lines[:-1])
  except:
    pass

  if igrow or imarks:
    p=subprocess.Popen('xml_archangel -a '+filename.split('.')[0]+'.xml marks', \
                        shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    lines='x y\n'
    for z in marks:
      lines=lines+str(z[0])+' '+str(z[1])+'\n'
    p.communicate(lines[:-1])

  if iap:
    p=subprocess.Popen('xml_archangel -a '+filename.split('.')[0]+'.xml apertures', \
                        shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    lines='x y r lum\n'
    for z in apertures:
      lines=lines+str(z[0])+' '+str(z[1])+' '+str(z[2])+' '+str(z[3])+'\n'
    p.communicate(lines[:-1])

def kill_pids(pids,kill_all):
  tmp=[]
  for z in pids:
    try:
      if z[1] or kill_all:
        os.kill(z[0],signal.SIGKILL) # god knows why the rxvt shell is pid+1, original shell is gone
        os.system('rm '+z[2])
      else:
        tmp.append(z)
    except:
      tmp.append(z)
  return tmp

def dump_marks():
  global prf_plot,clean,marks,lbl,scan,prf,verts,iwrite,sky,igrow,imarks,grow_mag,elements,apertures,iap
  global ft,cid,channel,markp,pids,geo,last_cmd,cmd,last_peek
  if imarks:
    for t in pids:
      if 'mark' in t[-1]:
        file=t[-1]
        break
    else:
      file=str(int(time.time()))+'_mark.tmp'
    fout=open(file,'w')
    fout.write('25\n')
    print >> fout,'         x           y     '
    for z in marks:
      print >> fout,'%10.0i' % (int(round(z[0])))+' '+'%11.0i' % (int(round(z[1]))),
      if abs(pix[int(round(z[1]))-1][int(round(z[0]))-1]) > 99999.:
        print >> fout,'%11.2e' % pix[int(round(z[1]))-1][int(round(z[0]))-1]
      else:
        print >> fout,'%11.2f' % pix[int(round(z[1]))-1][int(round(z[0]))-1]
      try:
        if pssii:
          tmp=map(float,os.popen('DSS_XY '+filename+' '+str(z[0])+' '+str(z[1])).read().split())
        else:
          tmp=xytosky(trans,z[0],z[1])
        if 'error' not in tmp:
          print >> fout,'%14.6f' % tmp[0]+'%11.6f' % tmp[1]+' ('+str(equinox)+')',
          print >> fout,hms(tmp[0],tmp[1])
      except:
        pass
    print >> fout,' '
    data=[]
    for z in marks:
      if pix[int(round(z[1]))-1][int(round(z[0]))-1] == pix[int(round(z[1]))-1][int(round(z[0]))-1]:
        data.append(pix[int(round(z[1]))-1][int(round(z[0]))-1])
    tmp=xits(data,3.)
    if 'NaN' not in tmp:
      print >> fout,'mean =','%.2f' % tmp[2],
      print >> fout,'sigm =','%.2f' % tmp[3],
      print >> fout,'max =','%.2f' % max(data),
      print >> fout,'min =','%.2f' % min(data)
    fout.close()
    if len(marks) == 1:
      p=subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/tterm.py -f cyan -r 26 -c 80 '+ \
        '-p '+geo['coord_window']+' '+os.environ['ARCHANGEL_HOME']+'/util/monitor.py '+file,shell=True)
      pids.append([p.pid+2,1,file])
  else:
    out=open('s.tmp','w')
    for x,y in marks:
      print >> out,x,y
    out.close()

def clicker(event): # primary event handler
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,middle,xsky,skysig,sig,filename,nmast,xd,yd,polly,inv
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
    tmp=float(str(hdr['CRPIX1']))
    tmp=tmp-(event.xdata-(i2-i1)/2)
    hdr.update('CRPIX1',tmp)
    tmp=float(str(hdr['CRPIX2']))
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
    if iwrite:
      prefix=filename.split('.')[0]
      if os.path.isfile(prefix+'.clean'): os.remove(prefix+'.clean')
      fitsobj2=pyfits.HDUList()
      hdu=pyfits.PrimaryHDU()
      hdu.header=hdr
      hdu.data=pix
      fitsobj2.append(hdu)
      fitsobj2.writeto(prefix+'.clean')
      fitsobj2.close()

    update_xml()

    if '-f' in sys.argv:
      if event.key in ['/','down']:
        nmast+=1
      else:
        nmast-=1
      if nmast >= len(master): nmast=0
      if nmast < 0: nmast=len(master)-1
      filename=master[nmast]
      max_width=0
      for t in pids:
        if 'files' in t[-1]:
          file=t[-1]
          break
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

#      channel.send(filename)
      get_data()
    else:
      disconnect(cid)
      close()
      if pids:
        pids=kill_pids(pids,0)
      time.sleep(0.5) # gluge to catch '/' before it passes it to nearest xwindow
      if '-v' in sys.argv: print 'clean exit',event.xdata,event.ydata
      sys.exit()

  elif event.key == 'G':
    fitsobj2=pyfits.HDUList()
    hdu=pyfits.PrimaryHDU()
    hdu.header=hdr
    hdu.data=pix[j1-1:j2,i1-1:i2]
    fitsobj2.append(hdu)
    fitsobj2.writeto(filename.split('.')[0]+'.snap')
    fitsobj2.close()

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
          rr=((polly[0][0]-event.xdata)**2.+(polly[0][1]-event.ydata)**2)**0.5
          try:
            lx=((polly[0][0]-polly[1][0])**2.+(polly[0][1]-polly[1][1])**2)**0.5
          except:
            lx=0.
          if rr < 0.1*lx:
            imin=1.e33 ; imax=-1.e33 ; jmin=1.e33 ; jmax=-1.e33
            for z in polly:
              if z[0] < imin: imin=int(z[0])
              if z[0] > imax: imax=int(z[0])
              if z[1] < jmin: jmin=int(z[1])
              if z[1] > jmax: jmax=int(z[1])
            for j in range(jmin,jmax):
              for i in range(imin,imax):
                if point_inside_polygon(i,j,polly): pix[j][i]=float('nan')
            del polly
          else:
            polly.append([event.xdata,event.ydata])

        except:
          polly=[[event.xdata,event.ydata]]

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

  elif event.key == 'w':
    update_xml()

  elif event.key in ['L']:
    fig_size=int(geo['main_size'])
    fig = figure(figsize=(fig_size, fig_size), dpi=80)
    draw_image()
#    draw()
    fig.savefig(filename.split('.')[0]+'_snap.pdf')
    print 'output to',filename.split('.')[0]+'_snap.pdf'

  elif event.key in ['h','H','J']:
    if not iap:
      iap=1
      tmp=os.popen('xml_archangel -o '+filename.split('.')[0]+' apertures').read()
      if 'element not found' in tmp:
        apertures=[(0.,0.,0.,0.)]
      else:
        apertures=[]
        scan=[]
        for t in tmp.split('\n')[1:-1]:
          aa=[]
          for z in t.split():
            aa.append(float(z))
          apertures.append(aa)
          scan.append((aa[0],aa[1],pi*aa[2]**2.,0.,0.,0.))
      prf_plot=-1

    else:
      if event.key == 'J':
        rmin=1.e33
        for i,z in enumerate(apertures):
          if ((event.xdata-z[0])**2+(event.ydata-z[1])**2)**0.5 < rmin:
            nmin=i
            rmin=((event.xdata-z[0])**2+(event.ydata-z[1])**2)**0.5
        del apertures[nmin]
        rmin=1.e33
        for i,z in enumerate(scan):
          if ((event.xdata-z[0])**2+(event.ydata-z[1])**2)**0.5 < rmin:
            nmin=i
            rmin=((event.xdata-z[0])**2+(event.ydata-z[1])**2)**0.5
        del scan[nmin]
      else:
        try:
          rx
          if ((event.xdata-rx[1])**2+(event.ydata-rx[2])**2)**0.5 > 5.: raise
        except:
#      tmp=os.popen('min_max '+filename+' '+str(event.xdata)+' '+str(event.ydata)+' 4').read()
#      t1=float(tmp.split()[13])
#      t2=float(tmp.split()[17])
#      t3=float(tmp.split()[21])

          d1=int(round(event.xdata)-1)
          d2=int(round(event.ydata)-1)
          t1=-1.e33
          for i in range(-3,2,1):
            for j in range(-3,2,1):
              if pix[d2+j][d1+i] >= t1:
                t1=pix[d2+j][d1+i]
                t2=d1+i+1
                t3=d2+j+1

          tmp=os.popen('gasp_images -f '+filename+' '+str(xsky)+' '+str(0.75*(t1-xsky))+' 4 true').read()
          for t in tmp.split('\n')[:-1]:
            if ((t2-float(t.split()[0]))**2+(t3-float(t.split()[1]))**2)**0.5 < 2.:
              break
          else:
            t=str(t2)+' '+str(t3)

#      ra=round(2.*(3.*(float(t.split()[2])/math.pi)**0.5),0)/2.

          ra=3. ; ibreak=0
          while (ra < 10.):
            for i in range(int(round(t2-ra))-1,int(round(t2+ra)),1):
              for j in range(int(round(t3-ra))-1,int(round(t3+ra)),1):
                if pix[j-1][i-1] < (5.*skysig+xsky):
                  ibreak=1
            if ibreak: break
            ra=ra+0.5

          rx=[ra,float(t.split()[0]),float(t.split()[1])]
          try:
            scan.append((0.,0.,0.,0.,0.,0.))
            apertures.append((0.,0.,0.,0.))
          except:
            scan=[(0.,0.,0.,0.,0.,0.)]
        if event.key == 'h':
          rx[0]=rx[0]+0.5
        else:
          rx[0]=rx[0]-0.5
        prf_plot=-1
        scan[-1]=(rx[1],rx[2],pi*rx[0]**2,0.,0.,0.)
        apertures[-1]=(rx[1],rx[2],rx[0],eapert(rx[1],rx[2],1.,0.,xsky,rx[0]))

  elif event.key == '?':
    fout=open('probe_data.tmp','w')
    fout.write(help()+'\n')
    fout.close()
    subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -text_window -x -f probe_data.tmp &',shell=True)

  elif event.key in ['x','X'] and prf_plot != 0:
    imin=find_imin(event.xdata,event.ydata)
    if event.key == 'X':
      if prf_plot == 1:
        del prf[imin]
        fout=open('tmp.prf','w')
        for z in prf:
          for t in z:
            print >> fout,'%16.8e' % (t),
          print >> fout,''
        fout.close()
        if os.path.isfile(filename.split('.')[0]+'.clean'):
          tmp=os.popen('iso_prf -q '+filename.split('.')[0]+'.clean tmp.prf -sg 0').read()
        else:
          tmp=os.popen('iso_prf -q '+filename+' tmp.prf -sg 0').read()
        os.system('rm tmp.prf')
        line='INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n'
        for z in tmp.split('\n')[:-1]:
          for t in z.split():
            line=line+t+' '
          line=line[:-1]+'\n'
        p=subprocess.Popen('xml_archangel -a '+filename.split('.')[0]+'.xml prf', \
                           shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        p.communicate(line)
      else:
        del scan[imin]
        file=open('s.tmp','w')
        format='%7.1f%7.1f%8.0f%7.3f%7.1f%11.4f'
        for t in scan:
          print >> file, format % tuple(t)
        file.close()
    else:
      prf[imin][6]=-99
    if prf_plot >= 1:
      eplot(prf)
    else:
      eplot(scan)

  elif event.key in ['o','k']:
    if event.key == 'o':
      clean_ellipses()
    else:
      imin=find_imin(event.xdata,event.ydata)
      smash_ellipses(imin)
    fout=open('tmp.prf','w')
    for z in prf:
      for t in z:
	print >> fout,'%16.8e' % (t),
      print >> fout,''
    fout.close()
    if os.path.isfile(filename.split('.')[0]+'.clean'):
      tmp=os.popen('iso_prf -q '+filename.split('.')[0]+'.clean tmp.prf -sg 0').read()
    else:
      tmp=os.popen('iso_prf -q '+filename+' tmp.prf -sg 0').read()
    os.system('rm tmp.prf')
    line='INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n'
    for z in tmp.split('\n')[:-1]:
      for t in z.split():
        line=line+t+' '
      line=line[:-1]+'\n'
    p=subprocess.Popen('xml_archangel -a '+filename.split('.')[0]+'.xml prf', \
                       shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    p.communicate(line)

  elif event.key == ';': # growth theshold
    imarks=0
    if not igrow:
      igrow=find_imin(event.xdata,event.ydata)
      sig=10.
      threshold(1.)
    else:
      k=0.5+(event.xdata-i1)/(i2-i1)
      threshold(k)

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

  elif event.key == 'e':
    try:
      lbl=[tmp.split() for tmp in open('s.tmp','r').readlines()]
      if ':' in lbl[0][0]:
        for n,z in enumerate(lbl):
          ra,dec=os.popen('hms '+lbl[n][0]+' '+lbl[n][1]).read().split()
          lbl[n][0],lbl[n][1]=skytoxy(trans,float(ra),float(dec))
    except:
      ft=figtext(0.1,0.05,'S.TMP FILE ERROR',horizontalalignment='left',verticalalignment='top',color='r')
      time.sleep(2)

  elif event.key == 'j':
    scan=[(map(float, tmp.split())) for tmp in open('s.tmp','r').readlines()]
    prf_plot=0
    imarks=1
    marks=[]
    for z in scan:
      marks.append((z[0],z[1]))
#    print 'doing marks',len(marks)

  elif event.key == '.':
    if (int(round(event.xdata)),int(round(event.ydata))) in marks:
      marks.remove((int(round(event.xdata)),int(round(event.ydata))))
    else:
      marks.append((int(round(event.xdata)),int(round(event.ydata))))
    imarks=1
    dump_marks()

  elif event.key == ',':
    if pids: pids=kill_pids(pids,1)
    imarks=0
    marks=[]

  elif event.key == '\\':
    for t in elements['array']:
      if t[0]['name'] == 'marks': # ellipse data
        marks=[]
        pts=[]
        for z in t[2]['axis']:
          pts.append(map(int,z[1].split('\n')))
        for z1,z2 in zip(pts[0],pts[1]):
          marks.append((z1,z2))

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

  elif event.key == 's':
    imarks=0  # turn off marks so sky boxes can draw
#    if event.key != last_cmd:
#      pids=kill_pids(pids,0)
#      file=str(int(time.time()))+'_sky.tmp'
#    else:
#      for t in pids:
#        if 'sky' in t[-1]: file=t[-1]

    try:
      for i,t in enumerate(sky):
        if event.xdata > t[4]-10 and event.xdata < t[4]+10 and event.ydata > t[5]-10 and event.ydata < t[5]+10:
          sky.remove(sky[i])
          draw_image()
          raise
      else:
        for t in sky:
          v=[(t[4]-10,t[5]-10),(t[4]+10,t[5]-10),(t[4]+10,t[5]+10),(t[4]-10,t[5]+10),(t[4]-10,t[5]-10)]
          poly=Polygon(v, fill=0, edgecolor='b')
          ax.add_patch(poly)
        v=[(int(round(event.xdata))-10,int(round(event.ydata))-10), \
                     (int(round(event.xdata))+10,int(round(event.ydata))-10), \
                     (int(round(event.xdata))+10,int(round(event.ydata))+10), \
                     (int(round(event.xdata))-10,int(round(event.ydata))+10), \
                     (int(round(event.xdata))-10,int(round(event.ydata))-10)]
        poly=Polygon(v, fill=0, edgecolor='b')
        ax.add_patch(poly)
        draw()
        data=[]
        for i in range(int(round(event.xdata))-10,int(round(event.xdata))+10,1):
          for j in range(int(round(event.ydata))-10,int(round(event.ydata))+10,1):
            try:
              data.append(pix[j][i])
            except:
              pass
        tmp=xits(data,3.)
        if str(sum(data)) != 'nan':
          sky.append((tmp[2],tmp[3],tmp[4],tmp[5],int(round(event.xdata)),int(round(event.ydata)),20,sum(data)))
    except:
      for t in sky:
        v=[(t[4]-10,t[5]-10),(t[4]+10,t[5]-10),(t[4]+10,t[5]+10),(t[4]-10,t[5]+10),(t[4]-10,t[5]-10)]
        poly=Polygon(v, fill=0, edgecolor='b')
        ax.add_patch(poly)

    data=[]
#    fout=open(file,'w')
#    fout.write('25\n')
#    print >> fout,'    mean   sig  dels    total     sky       skysig      x      y  box'
    for i,t in enumerate(sky):
#      print >> fout,'%8.2f' % t[0],'%6.2f' % t[1],'%4.1i' % (t[2]-t[3]),'%8.1f' % t[-1],
      data.append(t[0])
      if i >= 1:
        try:
          xsky=xits(data,3.)[2]
#          print >> fout,'%8.2f' % xsky,'+/-',
          skysig=xits(data,3.)[3] # look for sigma on sky means
#          print >> fout,'%7.2f' % skysig,
        except:
          pass
#          print >> fout,'%8.2f' % sky[-1][0],'+/-',
#          print >> fout,'%7.2f' % sky[-1][1],
      else:
        pass
#        print >> fout,'         +/-        ',
#      print >> fout,'%6.0i' % t[4],'%6.0i' % t[5],'  20'
#    fout.close()

    if event.key != last_cmd:
      pass
#      p=subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/tterm.py -f red -r 25 -c 80 '+ \
#        '-p '+geo['sky_window']+' '+os.environ['ARCHANGEL_HOME']+'/util/monitor.py '+file,shell=True)
#      pids.append([p.pid+2,1,file])
#      p=subprocess.Popen('/usr/local/bin/rxvt -fn 6x13 -bg black -fg red +sb -cr black -T "Sky Measurements"'+ \
#                         ' -geometry 75x26'+geo['sky_window']+' -e '+os.environ['ARCHANGEL_HOME']+'/util/monitor.py '+ \
#                         file+' &',shell=True)
#      pids.append([p.pid+1,1,file])

  elif event.key == 'P':
    k=0.5+(event.xdata-i1)/(i2-i1)
    sig=sig*k
    dum=str(i1)+','+str(i2)+','+str(j1)+','+str(j2)
    tmp=os.popen('peak '+filename+' '+dum+' '+str(skysig*sig+xsky)).read()
#    print 'peak '+filename+' '+dum+' '+str(skysig*sig+xsky)
    if scan:
#      print 'before',len(scan)
      for t in scan:
        if t[0] > i1 and t[0] < i2 and t[1] > j1 and t[1] < j2: scan.remove(t)
#      print 'after',len(scan)
    for t in tmp.split('\n')[:-1]:
#      print 't',t
      for z in scan:
        if ((z[0]-float(t.split()[0]))**2.+(z[1]-float(t.split()[1]))**2.)**0.5 < 1.5:
#          print 'break',z
          break
      else:
#        print 'else'
        scan.append(map(float, t.split()))
#    print 'added',len(scan)
    out=open('peaks'+filename.split('.')[0]+'.tmp','w')
    try:
      for t in scan:
        out.write(' '.join([str(dum) for dum in t])+'\n')
    except:
      raise
    out.close()
    prf_plot=-1

  elif event.key == 'I':
    k=0.5+(event.xdata-i1)/(i2-i1)
    sig=sig*k
#    print 'gasp_images -f '+filename+' '+str(xsky)+' '+str(skysig*sig)+' 5 true'
    tmp=os.popen('gasp_images -f '+filename+' '+str(xsky)+' '+str(skysig*sig)+' 5 true').read()
    scan=[]
    out=open('s.tmp','w')
    tail=' a'+'%.2f' % (skysig+sig)
    for t in tmp.split('\n')[:-1]:
      out.write(t+tail+'\n')
      scan.append(map(float, t.split()))
    out.close()
    for t in scan:
      if t[3] == 1. or t[3] == 0.: scan.remove(t)
    prf_plot=-1

  elif event.key == 'i':
    try:
      scan=[(map(float, tmp.split())) for tmp in open('s.tmp','r').readlines()]
      def determine(t):
        if len(t) == 0 or t[3] > 0.999: return False
        return True
      scan[:] = [t for t in scan if determine(t)]
      prf_plot=-1
    except:
      ft=figtext(0.1,0.05,'S.TMP FILE ERROR',horizontalalignment='left',verticalalignment='top',color='r')
      time.sleep(2)

  elif event.key in ['d']:
    if not scan:
      scan=[]
      prf_plot=-1
    for t in scan:
      if ((t[0]-event.xdata)**2.+(t[1]-event.ydata)**2)**0.5 < 2.:
        scan.remove(t)
        break
    else:
      pmax=0. ; ip=0 ; jp=0
      for j in range(int(event.ydata),int(event.ydata)+2,1):
        for i in range(int(event.xdata),int(event.xdata)+2,1):
          if pix[j-1][i-1] > pmax:
            pmax=pix[j-1][i-1] ; ip=i ; jp=j
      xc,yc=os.popen('centroid '+filename+' '+str(ip)+' '+str(jp)+' 5 ').read().split()
      scan.append([float(xc),float(yc),10,0.,0.,0.])

    out=open('peaks'+filename.split('.')[0]+'.tmp','w')
    for t in scan:
      tmp=''
      for z in t:
        tmp=tmp+' '+'%.2f' % z
      out.write(tmp+'\n')
    out.close()

  elif event.key in ['y','f']:
    clean=abs(abs(clean)-1)
    if event.key == 'y' and clean and os.path.isfile(filename.split('.')[0]+'.clean'):
      fitsobj=pyfits.open(filename.split('.')[0]+'.clean',"readonly")
    elif event.key == 'f' and clean and os.path.isfile(filename.split('.')[0]+'.fake'):
      fitsobj=pyfits.open(filename.split('.')[0]+'.fake',"readonly")
      clean=-1
    else:
      clean=0
      fitsobj=pyfits.open(filename,"readonly")
    hdr=fitsobj[0].header
    pix=fitsobj[0].data
    fitsobj.close()

  elif event.key in ['t','u']:
    if event.key == 'u':
      prf_plot=2
    else:
      if prf_plot:
        prf_plot=0
      else:
        prf_plot=1
#      if type(prf) == type([]): prf_plot=abs(prf_plot-1)
    if prf_plot: last_peek=find_imin(event.xdata,event.ydata)

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
        i2=min(int(2*xstep+i1),nx)
      if i2 > nx:
        i1=max(1,int(nx-2*xstep))
        i2=nx
      j1=int(round((event.ydata)-xstep))
      j2=int(round((event.ydata)+xstep))
      if j1 < 1:
        j1=1
        j2=min(int(2*xstep+j1),ny)
      if j2 > ny:
        j1=max(int(ny-2*xstep),1)
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
