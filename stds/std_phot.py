#!/usr/bin/env python

import pyfits,sys,os
import numarray
from ppgplot import *
from math import *
from xml_archangel import *

# quick display program ala prf_edit, enter a list of files or -f image
# first look for profile.py routine, aborts or output new options

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

def ap_sky(xc,yc,rr,dr):
  data=[]
  left=max(0,int(xc-rr-dr-5))
  right=min(int(xc+rr+dr+5),nx)
  bottom=max(0,int(yc-rr-dr-5))
  top=min(int(yc+rr+dr+5),ny)
  for x in numarray.arange(left,right,1):
    for y in numarray.arange(bottom,top,1):
      if ((x-xc)**2+(y-yc)**2)**0.5 > rr and ((x-xc)**2+(y-yc)**2)**0.5 <= rr+dr:
        if str(pix[y-1][x-1]) != 'nan': data.append(pix[y-1][x-1])
  return xits(data,3.)

def eapert(xc,yc,eps,th,xsky,rr):

  data=[]
  old_area=0.

  left=max(0,int(xc-rr-5))
  right=min(int(xc+rr+5),nx)
  bottom=max(0,int(yc-rr-5))
  top=min(int(yc+rr+5),ny)

  sum=0.
  tsum=0.
  npts=0.
  tot_npts=0.

  for x in numarray.arange(left,right,1):
    for y in numarray.arange(bottom,top,1):
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

  return -2.5*log10(sum)

def scan_plot(scan,icol):
  pgsci(icol)
  for ell in scan:
    if len(ell) < 1:
      icol+=1
      pgsci(icol)
      continue
    eps=1.-float(ell[3])
    if eps == 0: eps=0.99
    a=0.5*(float(ell[2])/(eps*pi))**0.5
    dd=(-float(ell[4]))*pi/180.
    xc=float(ell[0])
    yc=float(ell[1])
    bsq=(eps*a)**2
    asq=a**2
    th=0.
    step=2.
    istep=int(360./step)+1
    for i in range(istep):
      th=th+step
      t=th*pi/180.
      c1=bsq*(cos(t))**2+asq*(sin(t))**2
      c2=(asq-bsq)*2*sin(t)*cos(t)
      c3=bsq*(sin(t))**2+asq*(cos(t))**2
      c4=asq*bsq
      r=(c4/(c1*(cos(dd))**2+c2*sin(dd)*cos(dd)+c3*(sin(dd))**2))**.5
      if th == step:
        pgmove(r*cos(t)+xc,r*sin(t)+yc)
      else:
        pgdraw(r*cos(t)+xc,r*sin(t)+yc)
  pgsci(1)

def xits(x,xsig):
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

def xytosky(trans,x,y):
  if len(trans) == 7:
    corr=cos(pi*(trans[3]+trans[5]*(y-trans[4]))/180.)
    return trans[0]+(trans[2]/corr)*(x-trans[1]),trans[3]+trans[5]*(y-trans[4]),
  else:
    corr=cos(pi*(trans[4]+trans[6]*(x-trans[1])+trans[7]*(y-trans[5]))/180.)
    return trans[0]+(trans[2]/corr)*(x-trans[1])+(trans[3]/corr)*(y-trans[5]), \
           trans[4]+trans[6]*(x-trans[1])+trans[7]*(y-trans[5])

def hms(ra,dec):
  ra=24.*ra/360.
  print '%2.2i' % int(round(ra,4))+'h',
  mn=60.*(ra-int(round(ra,4)))
  print '%2.2i' % int(round(mn,2))+'m',
  sec=60.*(mn-int(round(mn,2)))
  if sec < 10:
    print '0'+'%3.1f' % abs(sec)+'s',
  else:
    print '%4.1f' % abs(sec)+'s',
  if dec < 0:
    sign='-'
  else:
    sign='+'
  dec=abs(dec)
  print sign+'%2.2i' % int(round(dec,4))+'d',
  mn=60.*(dec-int(round(dec,4)))
  print '%2.2i' % int(round(mn,2))+'m',
  sec=60.*(mn-int(round(mn,2)))
  if sec < 10:
    print '0'+'%3.1f' % abs(sec)+'s',
  else:
    print '%4.1f' % abs(sec)+'s',

def asinh(x):
  return log(x+(x**2 + 1)**0.5)

def edraw(eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  th=0.
  step=2.
  istep=int(360./step)+1
  for i in range(istep):
    th=th+step
    t=th*pi/180.
    c1=bsq*(cos(t))**2+asq*(sin(t))**2
    c2=(asq-bsq)*2*sin(t)*cos(t)
    c3=bsq*(sin(t))**2+asq*(cos(t))**2
    c4=asq*bsq
    r=(c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**.5
    if th == step:
      pgmove(r*cos(t)+xc,r*sin(t)+yc)
    else:
      pgdraw(r*cos(t)+xc,r*sin(t)+yc)
  return

def gray(pix,i1,i2,j1,j2,r1,r2):
  pgeras()
  pgpap(10.,aspect)
  pgswin(i1,i2,j1,j2)
  pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
  pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  pgptxt((i2-i1)/2.+i1+1.5,0.05*(j2-j1)+(j2+1.5),0.,0.5,filename)
  tmp='%6.1f' % r2
  pgptxt(i1+1.5,(j1+1.5)-0.10*(j2-j1),0.,0.5,tmp)
  tmp='%6.1f' % r1
  pgptxt(i2+1.5,(j1+1.5)-0.10*(j2-j1),0.,0.5,tmp)
  return

# main

if len(sys.argv) <= 1 or sys.argv[1] == '-h':
  print 'Usage: std_plot option master_file'
  print
  print 'do photometry of standards, currently set for 2.1m'
  print
  sys.exit()

pgbeg('/xs',1,1)
pgask(0)
pgscr(0,1.,1.,1.)
pgscr(1,0.,0.,0.)
pgscf(2)
pgsch(1.0)

master=os.popen('ls '+sys.argv[-1]+'*').read().split('\n')[:-1]

for filename in master:

  try:
    fitsobj=pyfits.open(filename,"readonly")
  except:
    print filename,'not found -- ABORTING'
    break
  nx=fitsobj[0].header['NAXIS1']
  ny=fitsobj[0].header['NAXIS2']
  aspect=float(ny)/nx
  hdr=fitsobj[0].header
  try:
    if 'POSSII' in hdr['SURVEY']:
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

  pix=fitsobj[0].data
  try:
    exptime=fitsobj[0].header['EXPTIME']
    filter=filename.split('_')[-1].replace('.fits','')
    airmass=fitsobj[0].header['AIRMASS']
  except:
    pass
  fitsobj.close()

  tmp=fitsobj[0].header['RA']
  ra=float(tmp.split(':')[0])+float(tmp.split(':')[1])/60.+float(tmp.split(':')[2])/3600.
  ra=360.*ra/24.
  tmp=fitsobj[0].header['DEC']
  dec=abs(float(tmp.split(':')[0]))+float(tmp.split(':')[1])/60.+float(tmp.split(':')[2])/3600.
  if '-' in tmp.split(':')[0]: dec=-dec

  plate=0.61

  if nx < 50:
    cmd='sky_box -s '+filename
  else:
    cmd='sky_box -f '+filename
  if 'SQIID' in hdr['INSTRUME']:
    cmd='sky_box -c '+filename+' 100 400 100 400'
  sky=os.popen(cmd).read()
  if len(sky) < 1 or 'error' in sky:
    print 'error in figuring out sky, aborting'
    sys.exit()
  xsky=float(sky.split()[2])
  skysig=float(sky.split()[3])

# set contrast values
  r1=xsky+50.*skysig
  r2=xsky-0.05*(r1-xsky)

# initialize edges, set write to zero
  i1=1
  i2=nx
  j1=1
  j2=ny
  xstep=nx/2
  x0=nx/2.
  y0=ny/2.
  xsig=5.
  iwrite=0
  stretch=0
  d=[0,0,sys.argv[1].replace('-','')]
  if filter in ['U','B','V','R','I']:
    std=open('/Users/js/stds/landolt.std_phot')
  else:
    std=open('/Users/js/stds/stone.std_phot')
  stds=[]
  while 1:
    line=std.readline()
    if not line: break
    t1=float(line.split()[1])+float(line.split()[2])/60.+float(line.split()[3])/3600.
    t1=360.*t1/24.
    t2=abs(float(line.split()[4]))+float(line.split()[5])/60.+float(line.split()[6])/3600.
    if '-' in line.split()[4]: t2=-t2
    stds.append([line.split()[0],t1,t2])
    if line.split()[0].lower() == sys.argv[-1][:-1].lower():
      ra=t1
      dec=t2
  std.close()

  dx=0. ; dy=0.
  while 1:
    gray(pix,i1,i2,j1,j2,r1,r2)
    pgsch(0.5)
    n=1
    for std in stds:
      if ra-plate*nx/(2.*3600.) < std[1] and ra+plate*nx/(2.*3600.) > std[1] and \
         dec-plate*ny/(2.*3600.) < std[2] and dec+plate*ny/(2.*3600.) > std[2]:
        if n:
          n=0
          pgsci(2)
          mx=(nx/2.)-3600.*(std[2]-dec)/plate
          my=(ny/2.)-3600.*(std[1]-ra)/plate
        else:
          pgsci(3)
        pgptxt((nx/2.)-3600.*(std[2]-dec)/plate+dx,(ny/2.)-3600.*(std[1]-ra)/plate+dy,0.,1.0,std[0])
    pgsch(1.0)
    pgsci(1)
    tmp=os.popen('gasp_images -f '+filename+' '+str(xsky)+' '+str(2.5*skysig)+' 20 true').read()
    scan=[]
    for t in tmp.split('\n'):
      if len(t.split()) > 2: scan.append(map(float,t.split()))
    print len(scan),'objects found, mark red target'
    scan_plot(scan,3)
    targets=[]
    for std in stds:
      if ra-plate*nx/(2.*3600.) < std[1] and ra+plate*nx/(2.*3600.) > std[1] and \
         dec-plate*ny/(2.*3600.) < std[2] and dec+plate*ny/(2.*3600.) > std[2]:
        x=(nx/2.)-3600.*(std[2]-dec)/plate+dx
        y=(ny/2.)-3600.*(std[1]-ra)/plate+dy
        rmin=1.e33
        for n,z in enumerate(scan):
          rr=((x-z[0])**2+(y-z[1])**2)**0.5
          if rr < rmin:
            rmin=rr
            imin=n
        targets.append([std[0],scan[imin][0],scan[imin][1],scan[imin][2]])

#    if not targets: continue
    d=pgband(0)
    if d[2] == '/': break
    dx=d[0]-mx
    dy=d[1]-my

  for star in targets:

    aspect=1.
    xstep=nx/6.
    i1=int(round(star[1]-xstep))-1
    i2=int(round(star[1]+xstep))-2
    if i1 < 1:
      i1=1
      i2=int(2*xstep+i1)
    if i2 > nx:
      i1=int(nx-2*xstep)
      i2=nx
    j1=int(round(star[2]-xstep))-1
    j2=int(round(star[2]+xstep))-2
    if j1 < 1:
      j1=1
      j2=int(2*xstep+j1)
    if j2 > ny:
      j1=int(ny-2*xstep)
      j2=ny

    gray(pix,i1,i2,j1,j2,r1,r2)
    pgsch(0.5)
    pgsci(2)
    for std in stds:
      if ra-plate*nx/(2.*3600.) < std[1] and ra+plate*nx/(2.*3600.) > std[1] and \
         dec-plate*ny/(2.*3600.) < std[2] and dec+plate*ny/(2.*3600.) > std[2]:
        if std[0] == star[0]: pgsci(4)
        pgptxt((nx/2.)-3600.*(std[2]-dec)/plate+dx,(ny/2.)-3600.*(std[1]-ra)/plate+dy,0.,1.0,std[0])
        pgsci(2)
    pgsch(1.0)
    pgsci(1)

    while 1:

      d=pgband(0)

      if d[2] == '\x03':
        print 'aborting'
        sys.exit(0)

      if d[2] == '/':
        break

      if d[2] == 'q':
        try:
          area=star[3]
          eps=1.
          th=0.
          xq=star[1]
          yq=star[2]
          rsky=45.
          drsky=15.
          xsky=ap_sky(xq,yq,rsky,drsky)[2]
          nsky=ap_sky(xq,yq,rsky,drsky)[5]
          rr=0.5*(area/(eps*pi))**0.5
          rr=0.85*rr+rr # moment radius up by 85%
        except:
          raise
          break
        while 1:
          area=eps*pi*(2.*rr)**2.
          gray(pix,i1,i2,j1,j2,r1,r2)
          scanx=[[xq,yq,area,1.-eps,th]]
          scan_plot(scanx,3)
          scanx=[[xq,yq,pi*rsky**2,0.,0.],[xq,yq,pi*(rsky+drsky)**2,0.,0.]]
          scan_plot(scanx,4)
          pgsci(4)
          pgptxt(i1+(i2-i1)/2.,j1+1.5*(j2-j1)/2.,0.,0.5,star[0])
          pgsci(1)
          os.system('clear')
          print
          print star[0]
          print
          for xr in numarray.arange(max(2.,rr-5.),rr,1.):
            phot=eapert(xq,yq,eps,th,xsky,xr)
            print '%6.1f' % xr,
            print '%7.3f' % phot
          print
          d=pgband(0)
          if d[2] in ['/','q']: break
          if d[2] == '+':
            rr+=1.
          elif d[2] == 's' or d[2] == 'w':
            if d[2] == 's':
              rsky=rsky+5.
            else:
              drsky=drsky+2.
            print 'old sky =','%.2f' % xsky,
            xsky=ap_sky(xq,yq,rsky,drsky)[2]
            print ' new sky =','%.2f' % xsky,nsky
            print
          elif d[2] == 'x':
            xq=d[0]
            yq=d[1]
          else:
            rr-=1.
        if d[2] == '/':
          file=open('std_phot.mags','a')
          file.write(star[0].ljust(15)+' '+filter.rjust(5)+' '+'%3.0f' % exptime+' '+'%4.2f' % airmass+ \
           ' '+'%6.1f' % rsky+' '+'%6.1f' % drsky+' '+'%6.1f' % rr+' '+'%7.3f' % phot+' '+os.getcwd()+'/'+filename+'\n')
          file.close()
          break

      if d[2] == 's':
        print
        sky=[]
        pgsci(4)
        print 'sky  sig dels total'
        while 1:
          data=[]
          pgmove(int(d[0]-10),int(d[1]-10))
          pgdraw(int(d[0]+10),int(d[1]-10))
          pgdraw(int(d[0]+10),int(d[1]+10))
          pgdraw(int(d[0]-10),int(d[1]+10))
          pgdraw(int(d[0]-10),int(d[1]-10))
          for i in range(int(d[0]-10),int(d[0]+10),1):
            for j in range(int(d[1]-10),int(d[1]+10),1):
              data.append(pix[j][i])
          sky.append(xits(data,3.))
          print '%.1f' % sky[-1][2],'%4.1f' % sky[-1][3],'%4.1i' % (sky[-1][4]-sky[-1][5]),'%.1f' % sum(data)
          d=pgband(0)
          if d[2] == '/': break
        print
        data=[]
        for t in sky:
          data.append(t[2])
        try:
          xsky=xits(data,3.)[2]
          print 'mean=','%.1f' % xsky,'+/-',
          data=[]
          for t in sky:
            data.append(t[3])
          skysig=xits(data,3.)[2]
          print '%.1f' % skysig
        except:
          pass
        pgsci(1)

      if d[2] == 'x':
        line='           Enter range: '
        pgswin(0.,1.,0.,1.)
        pgptxt(0.,-.1,0.,0.,line)
        tmp=''
        while 1:
          d=pgband(0)
          if d[2] == '\r':
            break
          else:
            pgsci(0)
            pgptxt(0.,-.1,0.,0.,line+tmp)
            if d[2] == '\b':
              tmp=tmp[:-1]
            else:
              tmp=tmp+d[2]
              pgswin(0.,1.,0.,1.)
              pgsci(1)
              pgptxt(0.,-.1,0.,0.,line)
            pgsci(1)
            pgptxt(0.,-.1,0.,0.,line+tmp)
        r2=float(tmp.split()[0])
        r1=float(tmp.split()[1])

      if d[2] == 'c':
        rold=r1
        k=0.5+(d[0]-i1)/(i2-i1)
        r1=r1*k
        if r1 < xsky: r1=(rold-xsky)/2.+xsky
        r2=xsky-0.05*(r1-xsky)

      if d[2] == 'r':
        aspect=float(ny)/nx
        xsig=0.
        xstep=nx/2
        i1=1
        i2=nx
        j1=1
        j2=ny
        pgswin(2,nx+1.0,2,ny+1.5)

      if d[2] == 'z' or d[2] == 'Z':
        aspect=1.
        if d[2] == 'z' and xstep > 4.: xstep=int(xstep/2)+1
        i1=int(round(d[0]-xstep))-1
        i2=int(round(d[0]+xstep))-2
        if i1 < 1:
          i1=1
          i2=int(2*xstep+i1)
        if i2 > nx:
          i1=int(nx-2*xstep)
          i2=nx
        j1=int(round(d[1]-xstep))-1
        j2=int(round(d[1]+xstep))-2
        if j1 < 1:
          j1=1
          j2=int(2*xstep+j1)
        if j2 > ny:
          j1=int(ny-2*xstep)
          j2=ny

      if d[2] == 'a' or d[2] in ['2','3','4','5','6','7','8','9']:
        xc=int(d[0])+0.5
        yc=int(d[1])+0.5
        if d[2] == 'a':
          d=pgband(0)
          r=((float(d[0])-xc)**2+(float(d[1])-yc)**2)**0.5
        else:
          r=float(d[2])
        for j in range(max(int(yc-r-2),0),min(int(yc+r+2),ny)):
          for i in range(max(int(xc-r-2),0),min(int(xc+r+2),nx)):
            rr=((i+1-xc)**2+(j+1-yc)**2)**0.5
            if rr < r: 
              pix[j][i]=float('nan')

      if d[2] == 'p':
        x1=max(int(d[0])-5,0)
        x2=min(int(d[0])+4,nx-1)
        y1=max(int(d[1])-5,0)
        y2=min(int(d[1])+4,ny-1)
        print
        print '    ',
        for i in xrange(x1,x2): print '%7.1i' % (i+1),
        print
        for j in xrange(y2,y1,-1):
          print '%5.1i' % (j+1),
          for i in xrange(x1,x2):
            print '%7.1f' % pix[j,i],
          print
        print

      if d[2] == '.':
        line='x = '+'%.2f' % d[0]+' y= '+'%.2f' % d[1]
        print line,
        print (40-len(line))*' ',
        print 'x =',int(round(d[0])),'y=',int(round(d[1]))
        try:
          if pssii:
            tmp=map(float,os.popen('DSS_XY '+filename+' '+str(d[0])+' '+str(d[1])).read().split())
            tmp2=map(float,os.popen('DSS_XY '+filename+' '+str(int(round(d[0])))+' '+str(int(round(d[1])))).read().split())
          else:
            tmp=xytosky(trans,d[0],d[1])
            tmp2=xytosky(trans,int(round(d[0])),int(round(d[1])))
          if 'error' not in tmp:
            line='%.6f' % tmp[0]+' '+'%.6f' % tmp[1]+' ('+str(equinox)+')'
            print line,
            print (40-len(line))*' ',
            print '%.6f' % tmp2[0],'%.6f' % tmp2[1],'('+str(equinox)+')'
            hms(tmp[0],tmp[1])
            print 12*' ',
            hms(tmp2[0],tmp2[1])
            print
            print
        except:
          pass

      gray(pix,i1,i2,j1,j2,r1,r2)
      pgsch(0.5)
      pgsci(2)
      for std in stds:
        if ra-plate*nx/(2.*3600.) < std[1] and ra+plate*nx/(2.*3600.) > std[1] and \
           dec-plate*ny/(2.*3600.) < std[2] and dec+plate*ny/(2.*3600.) > std[2]:
          if std[0] == star[0]: pgsci(4)
          pgptxt((nx/2.)-3600.*(std[2]-dec)/plate+dx,(ny/2.)-3600.*(std[1]-ra)/plate+dy,0.,1.0,std[0])
          pgsci(2)
      pgsch(1.0)
      pgsci(1)
