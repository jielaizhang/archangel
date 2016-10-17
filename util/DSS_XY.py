#!/usr/bin/env python

# this routine takes a FITS file and XY coord on frame and returns RA and Dec

import pyfits,sys,math

try:

  if sys.argv[1] == '-f':
    tab=pyfits.open(sys.argv[2])
  else:
    tab=pyfits.open(sys.argv[1])

  hdr=tab[0].header
#for n in hdr.ascardlist():
#  print n

# where Xc and Yc are the plate center coordinates in microns (assigned to keywords PPO3 and PPO6, respectively, in
# the FITS header) and Px and Py are the x and y dimensions of a pixel in microns (assigned to keywords XPIXELSZ and
# YPIXELSZ,respectively, in the FITS header).

  xc=hdr['PPO3']
  yc=hdr['PPO6']
  px=hdr['XPIXELSZ']
  py=hdr['YPIXELSZ']
  xoff=hdr['CNPIX1']
  yoff=hdr['CNPIX2']
  ac=hdr['PLTRAH']+hdr['PLTRAM']/60.+hdr['PLTRAS']/3600.
  ac=360.*ac/24.
  if hdr['PLTDECSN'] == '+':
    dc=hdr['PLTDECD']+hdr['PLTDECM']/60.+hdr['PLTDECS']/3600.
  else:
    dc=-1.*(hdr['PLTDECD']+hdr['PLTDECM']/60.+hdr['PLTDECS']/3600.)
  ac=math.pi*ac/180.
  dc=math.pi*dc/180.

  if sys.argv[1] == '-f':
    data=[map(float,tmp.split()) for tmp in open(sys.argv[-1],'r').readlines()]
  else:
    data=[]
    data.append([float(sys.argv[-2]),float(sys.argv[-1])])

  for z in data:
    xo=z[0]+xoff-0.5
    yo=z[1]+yoff-0.5
    x=(xc-px*xo)/1000.
    y=(py*yo-yc)/1000.

# One then constructs the standard coordinates xi, eta (x^2 = x*x):

#   xi  = A1*x + A2*y + A3 + A4*x^2 + A5*x*y + A6*y^2 + 
#         A7*(x^2 + y^2) + A8*x^3 + A9*x^2*y + A10*x*y^2 + 
#         A11*y^3 + A12 x*(x^2 + y^2) + A13*x*(x^2 + y^2)^2
 
#   eta = B1*y + B2*x + B3 + B4*y^2 + B5*x*y + B6*x^2 + 
#         B7*(x^2 + y^2) + B8*y^3 + B9*x*y^2 + B10*x^2*y + 
#         B11*x^3 + B12*y*(x^2 + y^2) + B13*y*(x^2 + y^2)^2

#where A1, ..., A13 are assigned to keywords AMDX1, ..., AMDX13 and B1, ...,B13 are assigned to keywords AMDY1, ...,
#AMDY13. The keywords AMDX14, ...,AMDX20 and AMDY14, ..., AMDY20 are not currently used. The standard coordinates,
#as computed above, will be in units of arcseconds.

    a=[]
    for n in range(13):
      i=n+1
      fld='AMDX'+'%1.0i' % i
      a.append(hdr[fld])
    xi=a[0]*x + a[1]*y + a[2] + a[3]*x**2 + a[4]*x*y + a[5]*y**2 
    xi=xi+a[6]*(x**2+y**2) + a[7]*x**3 + a[8]*y*x**2 + a[9]*x*y**2
    xi=xi+a[10]*y**3 + a[11]*x*(x**2+y**2) + a[12]*x*(x**2+y**2)**2
    xi=xi/3600.

    b=[]
    for n in range(13):
      i=n+1
      fld='AMDY'+'%1.0i' % i
      b.append(hdr[fld])
    eta=b[0]*y + b[1]*x + b[2] + b[3]*y**2 + b[4]*x*y + b[5]*x**2 
    eta=eta+b[6]*(x**2+y**2) + b[7]*y**3 + b[8]*x*y**2 + b[9]*y*x**2
    eta=eta+b[10]*x**3 + b[11]*y*(x**2+y**2) + b[12]*y*(x**2+y**2)**2
    eta=eta/3600.

    eta=math.pi*eta/180.
    xi=math.pi*xi/180.

#Finally, the J2000 celestial coordinates alpha, delta (in radians) are computed from the standard coordinates as
#follows:

    alpha = math.atan((xi/math.cos(dc))/(1.-eta*math.tan(dc)))+ac
    delta = math.atan(((eta+math.tan(dc))*math.cos(alpha-ac))/(1.-eta*math.tan(dc)))

#    if sys.argv[1] == '-f': print z[2],z[3],
    print '%10.6f' % (180.*alpha/math.pi),
    print '%10.6f' % (180.*delta/math.pi)

#print (180.*alpha/math.pi-float(sys.argv[4]))*3600.,(180.*delta/math.pi-float(sys.argv[5]))*3600.

#where Ac is the plate center right ascension (assigned to keywords PLTRAH,PLTRAM, and PLTRAS) and Dc is the plate
#center declination (assigned to keywords PLTDECSN, PLTDECD, PLTDECM, and PLTDECS).
#Attention! The variables Ac,Dc, xi, and eta must be converted to radians before using the above expressions! If
#alpha < 0, one must add 2 pi to its value to get the correct right ascension. 

except:
  print 'error no position information found'
