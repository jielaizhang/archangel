#!/usr/bin/env python

import pyfits,sys,os
from math import *
from xml_archangel import *
from pylab import *
from matfunc import *
from matplotlib.ticker import MultipleLocator # needed to fix up minor ticks
from matplotlib.patches import Ellipse, Polygon

import numpy as numarray

def rat_calc(xrat,arat,degree):
  nrat=0.
  for i in range(degree+1):
    nrat=nrat+arat[i]*xrat**(degree-i)
  drat=1.
  for i in range(1,degree+1):
    drat=drat+arat[i+degree]*xrat**(degree-i+1)
  return nrat/drat

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


def eplot(prf,icol):
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,xsky,skysig,filename,nmast,xd,yd,mask
  global ft,cid,channel,markp,pids,geo,last_cmd
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy
  global master,stds,nstar,targets,dx,dy,mx,my,ra,dec,plate,star,rsky,drsky,rr,phot,area,eps,th,xq,yq,rr,nsky,coeff,asym_mag

  if len(prf[0]) > 7:
    ells=[Ellipse((l[14],l[15]),2.*l[3],2.*l[3]*(1.-l[12]),l[13],fill=0) for l in prf]
  else:
    ells=[Ellipse((l[0],l[1]),(l[2]/(math.pi*(1.-l[3])))**0.5, \
                  (1.-l[3])*((l[2]/(math.pi*(1.-l[3])))**0.5),l[4],fill=0) for l in prf]
  for e,l in zip(ells,prf):
    e.set_clip_box(ax.bbox)
    e.set_alpha(1.0)
    e.set_edgecolor(icol)
    ax.add_artist(e)
  ax.set_xlim(i1-0.5,i2+0.5)
  ax.set_ylim(j1-0.5,j2+0.5)

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

def draw_image():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,xsky,skysig,filename,nmast,xd,yd,mask
  global prf_plot,clean,prf,prf2,verts,iwrite,sky
  global ft,cid,channel,markp,pids,geo,last_cmd
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy
  global master,stds,nstar,targets,dx,dy,mx,my,ra,dec,plate,star,rsky,drsky,rr,phot,area,eps,th,xq,yq,rr,nsky,coeff,asym_mag

  clf() ; ax = fig.add_subplot(111)

# pix will be down one in python coords from normal IRAF coords
# iraf[x,y] = pix[y-1][x-1]
# to plot x,y at center of pixel extent is -0.5

  palette=cm.gray
#  palette.set_over('b', 1.0)
#  palette.set_under('g', 1.0)
  palette.set_bad('r', 1.0)
  zm=ma.masked_where(isnan(pix[j1-1:j2,i1-1:i2]), pix[j1-1:j2,i1-1:i2])
  imshow(-zm,vmin=-r1,vmax=-r2,extent=(i1-0.5,i2+0.5,j1-0.5,j2+0.5), \
         aspect='equal',origin='lower',interpolation='nearest',cmap=palette)
#  imshow(-pix[j1-1:j2,i1-1:i2],vmin=-r1,vmax=-r2,extent=(i1-0.5,i2+0.5,j1-0.5,j2+0.5), \
#         aspect='equal',origin='lower',interpolation='nearest')

  tick=ticks(ax.xaxis.get_majorticklocs()[0],ax.xaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  ax.xaxis.set_minor_locator(minorLocator)
  tick=ticks(ax.yaxis.get_majorticklocs()[0],ax.yaxis.get_majorticklocs()[1])
  minorLocator   = MultipleLocator(tick)
  ax.yaxis.set_minor_locator(minorLocator)
  suptitle(filename)
  ft=figtext(0.13,0.91,'%.1f' % r2,horizontalalignment='left',verticalalignment='top',color='b')
  ft=figtext(0.90,0.91,'%.1f' % r1,horizontalalignment='right',verticalalignment='top',color='b')
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

  n=1
  for std in stds:
    if ra-plate*nx/(2.*3600.) < std[1] and ra+plate*nx/(2.*3600.) > std[1] and \
       dec-plate*ny/(2.*3600.) < std[2] and dec+plate*ny/(2.*3600.) > std[2]:
      if n:
        n=0
        mx=(nx/2.)-3600.*(std[2]-dec)/plate
        my=(ny/2.)-3600.*(std[1]-ra)/plate
        text((nx/2.)-3600.*(std[2]-dec)/plate+dx,(ny/2.)-3600.*(std[1]-ra)/plate+dy,std[0], \
               color='r',horizontalalignment='center',verticalalignment='center',fontsize=14)
      else:
        text((nx/2.)-3600.*(std[2]-dec)/plate+dx,(ny/2.)-3600.*(std[1]-ra)/plate+dy,std[0], \
               color='b',horizontalalignment='center',verticalalignment='center',fontsize=14)
  ax.set_xlim(i1-0.5,i2+0.5)
  ax.set_ylim(j1-0.5,j2+0.5)
  draw()

def draw_phot():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,xsky,skysig,filename,nmast,xd,yd,mask
  global ft,cid,channel,markp,pids,geo,last_cmd
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy
  global master,stds,nstar,targets,dx,dy,mx,my,ra,dec,plate,star,rsky,drsky,rr,phot,area,eps,th,xq,yq,rr,nsky,coeff,asym_mag

  try:
    tmp=phot.ravel()
    ax2 = axes([.62,.15,.25,.25])
    tmp.shape=(len(phot.ravel())/2,2)

#    fit=numarray.array([tmp.transpose()[0],tmp.transpose()[1]])
#    ap,bp,cp=polyfit(fit,2)
#    x0=-bp/(2.*ap)
#    pts=numarray.reshape(numarray.array(tmp.transpose()[0]+tmp.transpose()[1]),(2,len(tmp.transpose()[0])))
    t1=[] ; t2=[]
    for t in phot:
      t1.append(t[0])
      t2.append(t[1])
    pts=numarray.reshape(numarray.array(t1+t2),(2,len(t1)))
    coeff=ratfit(pts)
    xstep=(max(tmp.transpose()[0])+0.10*(max(tmp.transpose()[0])-min(tmp.transpose()[0]))- \
           min(tmp.transpose()[0])-0.10*(max(tmp.transpose()[0])-min(tmp.transpose()[0])))/100.
    x=[] ; z=[]
    for t in arange(min(tmp.transpose()[0])-0.10*(max(tmp.transpose()[0])-min(tmp.transpose()[0])), \
                    max(tmp.transpose()[0])+0.10*(max(tmp.transpose()[0])-min(tmp.transpose()[0])),xstep):
      x.append(t)
      z.append(rat_calc(t,coeff,2))
#      z.append(ap*t**2+bp*t+cp)
    ax2.plot(x,z,'r-')
    if coeff[0]/coeff[3] < phot[-1][1]:
      asym_mag=phot[-5][1]
    else:
      asym_mag=coeff[0]/coeff[3]
    ax2.plot([min(tmp.transpose()[0][2:])-0.10*(max(tmp.transpose()[0][2:])-min(tmp.transpose()[0][2:])), \
              max(tmp.transpose()[0][2:])+0.10*(max(tmp.transpose()[0][2:])-min(tmp.transpose()[0][2:]))], \
             [asym_mag,asym_mag],'g--')
    ax2.scatter(tmp.transpose()[0][2:],tmp.transpose()[1][2:],marker=(6,2,0),color='b')
    ax2.set_xlim(min(tmp.transpose()[0][2:])-0.10*(max(tmp.transpose()[0][2:])-min(tmp.transpose()[0][2:])),
                 max(tmp.transpose()[0][2:])+0.10*(max(tmp.transpose()[0][2:])-min(tmp.transpose()[0][2:])))
    ax2.set_ylim(max(tmp.transpose()[1][2:])+0.10*(max(tmp.transpose()[1][2:])-min(tmp.transpose()[1][2:])),
                 min(tmp.transpose()[1][2:])-0.10*(max(tmp.transpose()[1][2:])-min(tmp.transpose()[1][2:])))
    draw()
  except:
    pass

def get_data():
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,xsky,skysig,filename,nmast,xd,yd,mask
  global prf_plot,clean,prf,prf2,verts,iwrite,sky
  global ft,cid,channel,markp,pids,geo,last_cmd
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy
  global master,stds,nstar,targets,dx,dy,mx,my,ra,dec,plate,star,rsky,drsky,rr,phot,area,eps,th,xq,yq,rr,nsky,coeff,asym_mag

  try:
    if master.index(filename)+1 >= len(master): raise SystemExit
    filename=master[master.index(filename)+1]
  except SystemExit:
    sys.exit()
  except:
    filename=master[0]

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
  try:
    pix=pix*mask
  except:
    pass

  try: # try and get some basic photometry information
    exptime=fitsobj[0].header['EXPTIME']
    try:
      filter=fitsobj[0].header['TELFILTE']
    except:
      filter=fitsobj[0].header['FILTERS']
    airmass=fitsobj[0].header['AIRMASS']
  except:
    pass

  if os.path.isfile('filter.list'):
    junk=[tmp[:-1] for tmp in open('filter.list','r').readlines()]
    filters=eval(junk[0])
    filter=filters[int(filter)]

  print 'found filter',filter
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

# 2.1m hack
  tmp=fitsobj[0].header['RA']
  ra=float(tmp.split(':')[0])+float(tmp.split(':')[1])/60.+float(tmp.split(':')[2])/3600.
  ra=360.*ra/24.
  tmp=fitsobj[0].header['DEC']
  dec=abs(float(tmp.split(':')[0]))+float(tmp.split(':')[1])/60.+float(tmp.split(':')[2])/3600.
  if '-' in tmp.split(':')[0]: dec=-dec
  plate=0.61

  fitsobj.close()

  if nx < 50:
    cmd='sky_box -s '+filename
  else:
    cmd='sky_box -f '+filename
  tmp=os.popen(cmd).read()
  if len(tmp) < 1 or 'error' in tmp: # need a manual sky switch someday
    print 'error in figuring out sky, aborting'
    sys.exit()
  xsky=float(tmp.split()[2])
  skysig=float(tmp.split()[3])

# set contrast values
  sig=50.
  if '-m' in sys.argv: # if we are doing many files, hold the contrast constant, adjust the sky
    try:
      d=r1-r2
      r2=xsky-0.05*(r1-xsky)
      r1=r2+d
    except: # unless, of course, it fucks up
      r1=xsky+sig*skysig
      r2=xsky-0.05*(r1-xsky)
  else: # normal files, just calculate it
    if '-c' in sys.argv:
      r2=float(sys.argv[sys.argv.index('-c')+1])
      r1=float(sys.argv[sys.argv.index('-c')+2])
    else:
      r1=xsky+sig*skysig
      r2=xsky-0.05*(r1-xsky)

# i1,i2,j1,j2,xstep set image edges and zoom
  i1=1
  i2=nx
  j1=1
  j2=ny
  xstep=nx/2

  dx=0. ; dy=0.

  tmp=os.popen('gasp_images -f '+filename+' '+str(xsky)+' '+str(2.5*skysig)+' 20 true').read()
  prf=[]
  for t in tmp.split('\n'):
    if len(t.split()) > 2 and float(t.split()[3]) < 1.: prf.append(map(float,t.split()))
  print len(prf),'objects found, mark red target'
  targets=[]

#  print ra,dec,plate,nx,ny
  for std in stds:
#    if 'BD' in std[0]:
#      print std[0], ra-plate*nx/(2.*3600.),std[1],ra+plate*nx/(2.*3600.),
#      print std[0], dec-plate*ny/(2.*3600.),std[2],dec+plate*ny/(2.*3600.)
    if ra-plate*nx/(2.*3600.) < std[1] and ra+plate*nx/(2.*3600.) > std[1] and \
       dec-plate*ny/(2.*3600.) < std[2] and dec+plate*ny/(2.*3600.) > std[2]:
      x=(nx/2.)-3600.*(std[2]-dec)/plate+dx
      y=(ny/2.)-3600.*(std[1]-ra)/plate+dy
      rmin=1.e33
      for n,z in enumerate(prf):
        rr=((x-z[0])**2+(y-z[1])**2)**0.5
        if rr < rmin:
          rmin=rr
          imin=n
      targets.append([std[0],prf[imin][0],prf[imin][1],prf[imin][2]])
#  print 'targets',targets

def clicker(event): # primary event handler
  global ax,pix,hdr,nx,ny,xstep,i1,i2,j1,j2,r1,r2,xsky,skysig,filename,nmast,xd,yd,mask
  global prf_plot,clean,prf,prf2,verts,iwrite,sky
  global ft,cid,channel,markp,pids,geo,last_cmd
  global pssii,trans,equinox,exptime,filter,airmass,ix,iy
  global master,stds,nstar,targets,dx,dy,mx,my,ra,dec,plate,star,rsky,drsky,rr,phot,area,eps,th,xq,yq,rr,nsky,coeff,asym_mag

  try:
    ix=int(round(event.xdata))
    iy=int(round(event.ydata))
  except:
    ix=0
    iy=0

  if event.key == 'X':
    dx=event.xdata-mx
    dy=event.ydata-my
    print 'dx,dy','%5.1f' % dx,'%5.1f' % dy
    nstar=-1
    targets=[]
    for std in stds:
      if ra-plate*nx/(2.*3600.) < std[1] and ra+plate*nx/(2.*3600.) > std[1] and \
         dec-plate*ny/(2.*3600.) < std[2] and dec+plate*ny/(2.*3600.) > std[2]:
        x=(nx/2.)-3600.*(std[2]-dec)/plate+dx
        y=(ny/2.)-3600.*(std[1]-ra)/plate+dy
        rmin=1.e33
        for n,z in enumerate(prf):
          rr=((x-z[0])**2+(y-z[1])**2)**0.5
          if rr < rmin:
            rmin=rr
            imin=n
        targets.append([std[0],prf[imin][0],prf[imin][1],prf[imin][2]])

  if event.key in ['/','q','w']:
    if event.key == 'w':
      tmp=raw_input(star[0].ljust(15)+'%7.3f' % asym_mag+' (zero to abort): ')
      if tmp != '':
        asym_mag=float(tmp)
    if event.key in ['/','w']:
      try:
        if asym_mag != 0.:
          file=open('std_phot.mags','a')
          print star[0].ljust(15)+' '+filter.rjust(5)+' '+'%3.0f' % exptime+' '+'%4.2f' % airmass+ \
          ' '+'%6.1f' % rsky+' '+'%6.1f' % drsky+' '+'%6.1f' % rr+' '+'%7.3f' % asym_mag+' '+os.getcwd()+'/'+filename
          file.write(star[0].ljust(15)+' '+filter.rjust(5)+' '+'%3.0f' % exptime+' '+'%4.2f' % airmass+ \
          ' '+'%6.1f' % rsky+' '+'%6.1f' % drsky+' '+'%6.1f' % rr+' '+'%7.3f' % asym_mag+' '+os.getcwd()+'/'+filename+'\n')
          file.close()
      except:
        pass
    nstar=nstar+1
    try:
      star=targets[nstar]
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
      area=star[3]
      eps=1.
      th=0.
      xq=star[1]
      yq=star[2]
      rsky=45.
      drsky=15.
      rr=0.5*(area/(eps*pi))**0.5
#      rr=0.85*rr+rr # moment radius up by 85%
      rr=int(2.*rr) # moment radius up by 85%
    except:
      mask=pix/pix
      get_data()
      del star ; del phot ; del coeff

  if event.key == '+':
    rr+=1.

  if event.key in ['s','S']:
    if event.key == 's':
      rsky=rsky+5.
    else:
      drsky=drsky+2.
    print 'old sky =','%.2f' % xsky,
    xsky=ap_sky(xq,yq,rsky,drsky)[2]
    print ' new sky =','%.2f' % xsky,nsky
    print

  if event.key == 'x':
    xq=event.xdata
    yq=event.ydata

  if event.key == 'c':
    rold=r1
    k=0.5+(event.xdata-i1)/(i2-i1)
    r1=r1*k
    if r1 < xsky: r1=(rold-xsky)/2.+xsky
    r2=xsky-0.05*(r1-xsky)

  if event.key in ['2','3','4','5','6','7','8','9']:
    xc=int(event.xdata)+0.5
    yc=int(event.ydata)+0.5
    r=float(event.key)
    for j in range(max(int(yc-r-2),0),min(int(yc+r+2),ny)):
      for i in range(max(int(xc-r-2),0),min(int(xc+r+2),nx)):
        rr=((i+1-xc)**2+(j+1-yc)**2)**0.5
        if rr < r: 
          pix[j][i]=float('nan')

  if event.key not in ['shift']:

    if event.key not in ['c','X','2','3','4','5','6','7','8','9']:
      try:
        print
        print star[0]+' ('+'%5.1f' % xq+','+'%5.1f' % yq+')'
        print
        xsky=ap_sky(xq,yq,rsky,drsky)[2]
        nsky=ap_sky(xq,yq,rsky,drsky)[5]
        area=eps*pi*(2.*rr)**2.
        prf=[[xq,yq,area,1.-eps,th]]
        prf2=[[xq,yq,pi*rsky**2,0.,0.],[xq,yq,pi*(rsky+drsky)**2,0.,0.]]

        tmp=[]
        for xr in numarray.arange(max(2.,rr-10.),20.,1.):
          tmp.append([xr,eapert(xq,yq,eps,th,xsky,xr)])
          if xr == rr:
            print '>',
          else:
            print ' ',
          print '%6.1f' % tmp[-1][0],
          print '%7.3f' % tmp[-1][1]
        print
        phot=numarray.array(tmp)
      except:
        pass

    draw_image()
    try:
      eplot(prf,'b')
      eplot(prf2,'r')
    except:
      pass
    draw_phot()
    if event.key not in ['c','X','2','3','4','5','6','7','8','9']:
      try:
        if coeff[0]/coeff[3] < phot[-1][1]:
          asym_mag=phot[-5][1]
          print 'asym mag=','%6.3f' % (coeff[0]/coeff[3]),'%6.3f' % asym_mag
        else:
          asym_mag=coeff[0]/coeff[3]
          print 'asym mag=','%6.3f' % asym_mag
      except:
        pass

# main

if len(sys.argv) <= 1 or sys.argv[1] == '-h':
  print 'Usage: std_plot option master_file'
  print
  print 'do photometry of standards, currently set for 2.1m'
  print
  sys.exit()

geo=eval(' '.join([tmp[:-1] for tmp in open(os.environ['ARCHANGEL_HOME']+'/.archangel','r').readlines()]))
fig_size=int(geo['main_size'])
fig = figure(figsize=(fig_size, fig_size), dpi=80)
ax = fig.add_subplot(111)
manager = get_current_fig_manager()
manager.window.title('')
manager.window.geometry(geo['main_window'])

#master=os.popen('ls '+sys.argv[-1]+'*').read().split('\n')[:-1]
master=[tmp[:-1] for tmp in open(sys.argv[-1],'r').readlines()]

nstar=-1

gray()
get_data()
draw_image()
eplot(prf,'g')

cid=connect('key_press_event',clicker)
show()
