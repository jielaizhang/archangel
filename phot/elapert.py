#!/usr/bin/env python

# elliptical apertures - see draw_apert for graphics version
# note that python array coords and IRAF coords are off
# by one pixel x/y and flipped; e.g. data(i,j) == pix[j-1][i-1]

import sys, os
from math import *
try:
  import numpy.numarray as numarray
except:
  import numarray
import pyfits
from xml_archangel import *

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

if sys.argv[1] == '-h':
  print 'elapert options fits_file'
  print
  print 'looks for .xml file for sky, calib, ellipse data'
  print
  print 'options:   -h = this message'
  print '         -sky = new sky value'
  print '         -fit = do not use fit information'
  sys.exit()

# runtime warnings in ellipse (?)
import warnings
warnings.filterwarnings('ignore')

fitsobj=pyfits.open(sys.argv[-1],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
aspect=1.
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()

if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
  doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
  rootNode = doc.documentElement
  elements=xml_read(rootNode).walk(rootNode)

  try:
    xsky=float(elements['sky'][0][1])
  except:
#    print 'sky value not found, setting to zero'
    xsky=0.
  try:
    skysig=float(elements['skysig'][0][1])
  except:
#    print 'skysig not found, setting to one'
    skysig=1.

  if '-sky' in sys.argv:
    xsky=float(sys.argv[sys.argv.index('-sky')+1])

  try:
    scale=float(elements['scale'][0][1])
  except:
#    print 'pixel scale value not found, setting to one'
    scale=1.

  try:
    zpt=float(elements['zeropoint'][0][1])
  except:
#    print 'zeropoint not found, setting to 25.'
    zpt=25.
  try:
    exptime=float(elements['exptime'][0][1])
  except:
    exptime=1.
  if exptime != 0.:
    try:
      k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05}
      airmass=k[elements['filter'][0][1]]*float(elements['airmass'][0][1])
    except:
      airmass=0.
    zpt=2.5*log10(exptime)-airmass+zpt

  try:
    cstore=float(elements['mu_o'][0][1])
    alpha=float(elements['alpha'][0][1])
    sstore=1.0857/alpha
  except:
    cstore=float('nan')
    sstore=float('nan')
  try:
    re=float(elements['re'][0][1])
    se=float(elements['se'][0][1])
  except:
    re=float('nan')
    se=float('nan')
#  if str(re) == 'nan' and str(cstore) == 'nan':
#    print 'no profile fit found, exp mags turned off'

  for t in elements['array']:
    if t[0]['name'] == 'prf':
      pts=[]
      for z in t[2]['axis']:
        pts.append(map(float,z[1].split('\n')))
      tmp=numarray.array(pts)
      pts=numarray.swapaxes(tmp,1,0)
      break

print '  radius          mag               area             xsfb           expm           kill'

data=[]
old_area=0.
for line in pts:

  if line[3] > 20.: break # stop for greater than 20 pixels, transfer to quick_elapert

  left=max(0,int(line[14]-line[3]-5))
  right=min(int(line[14]+line[3]+5),nx)
  bottom=max(0,int(line[15]-line[3]-5))
  top=min(int(line[15]+line[3]+5),ny)

  sum=0.
  npts=0.
  tot_npts=0.
  if line[3] < 3: 
    old_int=line[0]
    continue

  for x in numarray.arange(left,right,1):
    for y in numarray.arange(bottom,top,1):
      area=0.
      tmp=inside(x,y,1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])
      vert=[]
      if tmp and len(tmp) < 4:
        y1,y2=ellipse('x',x-0.5,line[3],(1.-line[12])*line[3], \
                      line[14],line[15],line[13]*pi/180.)
        if str(y1) != 'nan' and str(y2) != 'nan':
          if ((y-y1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x-0.5,y1))
          if ((y-y2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x-0.5,y2))
        y1,y2=ellipse('x',x+0.5,line[3],(1.-line[12])*line[3], \
                      line[14],line[15],line[13]*pi/180.)
        if str(y1) != 'nan' and str(y2) != 'nan':
          if ((y-y1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x+0.5,y1))
          if ((y-y2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x+0.5,y2))
        x1,x2=ellipse('y',y-0.5,line[3],(1.-line[12])*line[3], \
                      line[14],line[15],line[13]*pi/180.)
        if str(x1) != 'nan' and str(x2) != 'nan':
          if ((x-x1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x1,y-0.5))
          if ((x-x2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x2,y-0.5))
        x1,x2=ellipse('y',y+0.5,line[3],(1.-line[12])*line[3], \
                      line[14],line[15],line[13]*pi/180.)
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
#      if area > 0: print x,y,area,pix[y-1][x-1],line[14],line[15]
# watch the pixel offset
      if str(pix[y-1][x-1]) != 'nan':
#        print sum,pix[y-1][x-1]
        sum=sum+area*(pix[y-1][x-1]-xsky)
        npts=npts+area
      tot_npts=tot_npts+area

  try:
    -2.5*log10(sum)
    print '%16.8e' % line[3],
    print '%16.8e' % (-2.5*log10(sum)),
    print '%16.8e' % npts,
    try:
      xsfb=((line[0]+old_int)/2.-xsky)*(tot_npts-old_area)
      print '%16.8e' % (-2.5*log10(xsfb)),

      if str(cstore) != 'nan':
        xnt=cstore+sstore*(line[3]*scale)
        xnt=-0.4*xnt
        xnt1=10.**(xnt)
      else:
        xnt1=0.

      if str(re) != 'nan':
        xnt=se+8.325*(((scale*line[3])/re)**0.25-1.)
        xnt=-0.4*xnt
        xnt2=10.**xnt
      else:
        xnt2=0.

      if xnt1 != 0 or xnt2 != 0:
        xnt=-2.5*log10(xnt1+xnt2)
        z=scale*scale*(10.**((xnt-zpt)/-2.5))
        z=z*(tot_npts-old_area)
        if '-fit' in sys.argv:
          print '%16.8e' % (-2.5*log10(xsfb)),
        else:
          print '%16.8e' % (-2.5*log10(z)),
        data.append(['%16.8e' % line[3],'%16.8e' % (-2.5*log10(sum)),'%16.8e' % npts,'%16.8e' % (-2.5*log10(xsfb)), \
                     '%16.8e' % (-2.5*log10(z))])
      else:
        data.append(['%16.8e' % line[3],'%16.8e' % (-2.5*log10(sum)),'%16.8e' % npts,'%16.8e' % (-2.5*log10(xsfb))])
        print '0.00000000E+00',
      print '1'

    except:
      print '  0.             0.             1'
  except:
    pass
  old_int=line[0]
  old_area=tot_npts

# old section for direct dump to xml file
#
#out=xml_write(sys.argv[-1].split('.')[0]+'.xml',rootNode.nodeName)
#try:
#  for t in elements['array']:
#    if t[0]['name'] == 'ept':
#      try:
#        del elements['array'][elements['array'].index(t)]
#      except:
#        pass
#  if not elements['array']: del elements['array']
#except:
#  pass
#
#out.loop(elements)
#out.dump('  <array name=\''+'ept'+'\'>\n')
#if len(data[0]) == 5:
#  header=['radius','mag','area','xsfb','expm']
#else:
#  header=['radius','mag','area','xsfb']
#for t in header:
#  out.dump('    <axis name=\''+t+'\'>\n')
#  for line in data:
#    out.dump('      '+line[header.index(t)]+'\n')
#  out.dump('    </axis>\n')
#out.dump('  </array>\n')
#out.close()
