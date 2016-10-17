#!/usr/bin/env python

import sys, os.path, pyfits
try:
  import numpy.numarray as numarray
except:
  import numarray
from matfunc import *
from ppgplot import *
from xml.dom import minidom, Node
from xml_archangel import *

def edraw(eps,a,d,xc,yc):
  pgsci(3)
  bsq=(eps*a)**2
  asq=a**2
  th=0.
  step=2.
  istep=int(360./step)+1
  for i in range(istep):
    th=th+step
    t=th*math.pi/180.
    c1=bsq*(math.cos(t))**2+asq*(math.sin(t))**2
    c2=(asq-bsq)*2*math.sin(t)*math.cos(t)
    c3=bsq*(math.sin(t))**2+asq*(math.cos(t))**2
    c4=asq*bsq
    r=(c4/(c1*(math.cos(d))**2+c2*math.sin(d)*math.cos(d)+c3*(math.sin(d))**2))**.5
    if th == step:
      pgmove(r*math.cos(t)+xc,r*math.sin(t)+yc)
    else:
      pgdraw(r*math.cos(t)+xc,r*math.sin(t)+yc)
  pgsci(1)
  return

def tiny_pic(xmin,xmax,ymin,ymax):
  h1,h2,h3,h4=pgqvp(1)
  e1,e2,e3,e4=pgqvp(0)
  p1=(e2-e1)/(h2-h1)
  p2=(e4-e3)/(h4-h3)
  f2=e2-0.05*(e2-e1)
  f1=f2-0.50*(e2-e1)
  f3=e3+0.05*(e4-e3)
  f4=f3+(p2/p1)*0.50*aspect*(e4-e3)
#  print f1,f2,f3,f4,float(ny)/nx
  i1=0 ; i2=nx ; j1=0 ; j2=ny
  pgsvp(f1,f2,f3,f4)
  pgswin(i1,i2,j1,j2)
  pggray_s(pix[j1+1:j2+1,i1+1:i2+1],r1,r2,i1,j1,i2,j2)
  pgswin(i1+1.5,i2+1.5,j1+1.5,j2+1.5)
  pgsch(0.4)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  edraw(1.-line[12],line[3],-line[13]*math.pi/180.,line[14],line[15])
  pgsch(1.0)
  pgsvp(e1,e2,e3,e4)
  pgswin(xmin,xmax,ymax,ymin)

def do_fit(x,lum):
  fit=numarray.array([x,lum])
  a,b,c=polyfit(fit,2)
  x0=-b/(2.*a)
  z=[]
  err=0.
  for t1,t2 in zip(x,lum):
    if t1 > x0:
      z.append(a*x0**2+b*x0+c)
      err=err+(t2-(a*x0**2+b*x0+c))**2
    else:
      z.append(a*t1**2+b*t1+c)
      err=err+(t2-(a*t1**2+b*t1+c))**2
  return z,a,b,c,x0,(err/len(x))**0.5

def rat_calc(x,a,degree):
  n=0.
  for i in range(degree+1):
    n=n+a[i]*x**(degree-i)
  d=1.
  for i in range(1,degree+1):
    d=d+a[i+degree]*x**(degree-i+1)
  return n/d

def min_max():
  x=[] ; y=[]
  for tmp in data:
    x.append(tmp[0])
    y.append(tmp[1])

  for tmp in data[:imin]:
    if not tmp[2]:
      x.append(tmp[0])
      y.append(tmp[1])
  xlum=10.**((data[imin-1][1]-zpt)/-2.5)
  for tmp in data[imin:]:
    if not tmp[2] and str(tmp[4]) != 'nan':
      xlum=xlum+10.**(tmp[4]/-2.5)
      x.append(tmp[0])
      y.append(-2.5*math.log10(xlum)+zpt)

  for tmp in data[:imin]:
    if tmp[2]:
      x.append(tmp[0])
      y.append(tmp[1])
  xlum=10.**((data[imin-1][1]-zpt)/-2.5)
  for tmp in data[imin:]:
    if tmp[2] and str(tmp[4]) != 'nan':
      xlum=xlum+10.**(tmp[4]/-2.5)
      x.append(tmp[0])
      y.append(-2.5*math.log10(xlum)+zpt)

  xmax=max(x)+0.10*(max(x)-xmin)
  ymin=min(y)-0.10*(ymax-min(y))
  return xmax,ymin

def plot():
  pgeras()
  pgsci(1)
  xmax,ymin=min_max()
  pgswin(xmin,xmax,ymax,ymin)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  pglab('log r','mag',sys.argv[-1].split('.')[0])

# mark start point for exp addition
  pgsci(9) # green
  pgsch(2.5)
  pgpt(numarray.array([data[imin][0]]),numarray.array([data[imin][1]]),4) # big circle
  pgsch(1.0)

# plot raw photometry datapoints
  pgsci(1)
  x=[] ; y=[]
  for tmp in data:
    if tmp[1] != top_lum:
      x.append(tmp[0])
      y.append(tmp[1])
  pgpt(numarray.array(x),numarray.array(y),12) # stars

  pgsci(4) # blue
# plot prf fitted datapoints
  x=[] ; lum=[]
  for tmp in data[:imin+1]: # sum lum until imin point reached
    if not tmp[2]:
      x.append(tmp[0])
      lum.append(tmp[1])
  xlum=10.**((data[imin][1]-zpt)/-2.5)
  for tmp in data[imin+1:]:
    if not tmp[2] and str(tmp[4]) != 'nan':
      xlum=xlum+10.**(tmp[4]/-2.5)
      x.append(tmp[0])
      lum.append(-2.5*math.log10(xlum)+zpt)
  pgpt(numarray.array(x),numarray.array(lum),3) # circles

# plot fit, in blue
  z,a,b,c,x1,err1=do_fit(x,lum)
  mag1=a*x1**2+b*x1+c
  pgline(numarray.array(x),numarray.array(z))
# mark position of zero slope point
  pgpt(numarray.array([x1]),numarray.array([ymin+0.03*(ymax-ymin)]),31)
#  err1=find_err()
  pgswin(0.,1.,0.,1.)
  tmp='%6.3f' % (mag1)+' +/- '+'%6.3g' % err1
  pgptxt(0.07,0.92,0.,0.,'Raw:')
  pgptxt(0.16,0.92,0.,0.,tmp)
  pgswin(xmin,xmax,ymax,ymin)

# plot prf unfitted data
  x=[] ; y=[]
  for tmp in data[:imin+1]:
    if tmp[2]:
      x.append(tmp[0])
      y.append(tmp[1])
  xlum=10.**((data[imin][1]-zpt)/-2.5)
  for tmp in data[imin+1:]:
    if tmp[2] and str(tmp[4]) != 'nan':
      xlum=xlum+10.**(tmp[4]/-2.5)
      x.append(tmp[0])
      y.append(-2.5*math.log10(xlum)+zpt)
  pgpt(numarray.array(x),numarray.array(y),3) # astericks

  pgsci(2) # red
# plot exp fitted datapoints
  x=[] ; lum=[]
  for tmp in data[:imin+1]:
    if not tmp[2]:
      x.append(tmp[0])
      lum.append(tmp[1])
  xlum=10.**((data[imin][1]-zpt)/-2.5)
  for tmp in data[imin+1:]:
    if not tmp[2] and str(tmp[5]) != 'nan':
      xlum=xlum+10.**(tmp[5]/-2.5)
      x.append(tmp[0])
      lum.append(-2.5*math.log10(xlum)+zpt)
  pgpt(numarray.array(x),numarray.array(lum),4) # circles

# plot fit
  z,a,b,c,x2,err2=do_fit(x,lum)
  mag2=a*x2**2+b*x2+c
  pgline(numarray.array(x),numarray.array(z))
# mark position of zero slope point
  pgpt(numarray.array([x2]),numarray.array([ymin+0.03*(ymax-ymin)]),31)
#  err2=find_err()
  pgswin(0.,1.,0.,1.)
  tmp='%6.3f' % (mag2)+' +/- '+'%6.3g' % err2
  pgptxt(0.07,0.88,0.,0.,'Exp:')
  pgptxt(0.16,0.88,0.,0.,tmp)
  pgswin(xmin,xmax,ymax,ymin)


  pgsci(6) # cyan
  pts=numarray.reshape(numarray.array(x+lum),(2,len(x)))
  coeff=ratfit(pts)
#  if coeff[4]**2-4.*coeff[3] > 0:
#    print 'undefined at',(-coeff[4]+(coeff[4]**2-4.*coeff[3])**0.5)/(2.*coeff[3])
#    pgswin(0.,1.,0.,1.)
#    pgptxt(0.07,0.84,0.,0.,'Asy:  NaN')
#    pgswin(xmin,xmax,ymax,ymin)
#    asym=float('nan')
#  else:
  pgmove(x[0],rat_calc(x[0],coeff,2))
  for tmp in x:
    pgdraw(tmp,rat_calc(tmp,coeff,2))
# using last point as asym mag
# math def is asym=coeff[0]/coeff[3]
  pgpt(numarray.array([xmax-0.04*(xmax-xmin)]),numarray.array([rat_calc(x[-1],coeff,2)]),28)
  asym=rat_calc(x[-1],coeff,2)
  tmp='%6.3f' % (asym)+' +/- '+'%6.3g' % err2
  pgswin(0.,1.,0.,1.)
  pgptxt(0.07,0.84,0.,0.,'Asy:')
  pgptxt(0.16,0.84,0.,0.,tmp)

  pgswin(xmin,xmax,ymax,ymin)

# this section draws a green extrapolation for every other raw data point
#  pgsci(3)
#  for n,t in enumerate(data[imin:]):
#    if n%2 == 0:
#      x=[] ; lum=[]
#      x.append(t[0])
#      xlum=10.**((data[n+imin][1]-zpt)/-2.5)
#      lum.append(-2.5*math.log10(xlum)+zpt)
#      for tmp in data[n+imin+1:]:
#        if not tmp[2] and str(tmp[5]) != 'nan':
#          xlum=xlum+10.**(tmp[5]/-2.5)
#          x.append(tmp[0])
#          lum.append(-2.5*math.log10(xlum)+zpt)
#      pgline(numarray.array(x),numarray.array(lum))

# plot prf unfitted data
  pgsci(2)
  x=[] ; y=[]
  for tmp in data[:imin+1]:
    if tmp[2]:
      x.append(tmp[0])
      y.append(tmp[1])
  xlum=10.**((data[imin][1]-zpt)/-2.5)
  for tmp in data[imin+1:]:
    xlum=xlum+10.**(tmp[5]/-2.5)
    if tmp[2]:
      x.append(tmp[0])
      y.append(-2.5*math.log10(xlum)+zpt)
  pgpt(numarray.array(x),numarray.array(y),3) # astericks

# plot error boundaries
#  pgsci(2)
#  x=[] ; y=[]
#  for tmp in data:
#    n=data.index(tmp)
#    x.append(tmp[0])
#    y.append(up[n]-data[n][1]+lum[n])
#  xs=numarray.array(x) ; ys=numarray.array(y)
#  pgline(xs,ys)
#  x=[] ; y=[]
#  for tmp in data:
#    n=data.index(tmp)
#    x.append(tmp[0])
#    y.append(down[n]-data[n][1]+lum[n])
#  xs=numarray.array(x) ; ys=numarray.array(y)
#  pgline(xs,ys)

  pgsci(1)
  tiny_pic(xmin,xmax,ymin,ymax)
  return mag1,mag2,x1,x2,err1,err2,asym

def find_err():
  l=0
  for n in range(len(data)):
    if data[n][0] > x0:
      l=n
      break
  t1=up[l]+(x0-data[l][0])*(up[l-1]-up[l])/(data[l-1][0]-data[l][0])
  t2=down[l]+(x0-data[l][0])*(down[l-1]-down[l])/(data[l-1][0]-data[l][0])
#  asym=a*x0**2+b*x0+c
#  return (abs(t1-asym)+abs(t2-asym))/2.
  return abs(t1-t2)/2.

if __name__ == '__main__':
  if sys.argv[1] == '-h':
    print 'Usage: asymptotic xml_file'
    print
    print 'simply GUI that determines asymptotic fit on integrated galaxy mag,'
    print 'delivers mag/errors from apertures and curve of growth fit into XML file'
    print
    print 'cursor commands:'
    print 'r = reset       a = adjust lum for better fit'
    print 'f = linear fit  x,1,2,3,4 = delete points'
    print 'z = set profile extrapolation point'
    print '/ = exit        b = change borders'
    sys.exit()

  pgbeg('/xs',1,1)
  pgask(0)
  pgscr(0,1.,1.,1.)
  pgscr(1,0.,0.,0.)
  pgscf(2)
  pgpap(11.0,1.0)

  if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
    doc = minidom.parse(sys.argv[-1].split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    try:
      sky=float(elements['sky'][0][1])
    except:
      print 'sky value not found, setting to zero'
      sky=0.
    try:
      skysig=float(elements['skysig'][0][1])
    except:
      print 'skysig not found, setting to one'
      skysig=1.
    try:
      nsky=int(elements['nsky'][0][1])
    except:
      print 'nsky value not found, setting to 1'
      nsky=1

    try:
      scale=float(elements['scale'][0][1])
    except:
      print 'pixel scale value not found, setting to one'
      scale=1.
    try:
      zpt=float(elements['zeropoint'][0][1])
    except:
      print 'zeropoint not found, setting to 25.'
      zpt=25.

    try:
      for t in elements['array']:
        if t[0]['name'] == 'ept':
          pts=[]
          for z in t[2]['axis']:
            pts.append(map(float,z[1].split('\n')))
          tmp=numarray.array(pts)
          pts=numarray.swapaxes(tmp,1,0)
          break
      else:
        print 'no ept data in .xml file - aborting'
        sys.exit()
    except:
      raise
      print 'problem with data in .xml file - aborting'
      sys.exit()

    data=[]
# storing log r (arcsecs), app mag, erase flag, number of pixels (for
# error), prf intensity, exp intensity

    top_lum=pts[-1][1]+zpt
    imin=0
    for n,line in enumerate(pts):
      if len(line) == 5:
        data.append([math.log10(scale*line[0]),
                     line[1]+zpt,
                     0,
                     line[2],
                     line[3],
                     line[4]])
      else:
        data.append([math.log10(scale*line[0]),
                     line[1]+zpt,
                     0,
                     line[2],
                     line[3],
                     0.])
      if not imin and line[1]+zpt == top_lum: imin=n-5

    for t in elements['array']:
       if t[0]['name'] == 'prf':
         prf=[]
         for z in t[2]['axis']:
           prf.append(map(float,z[1].split('\n')))
         tmp=numarray.array(prf)
         prf=numarray.swapaxes(tmp,1,0)

  else:
    print 'no .xml file'
    sys.exit()

  fitsobj=pyfits.open(sys.argv[-1].split('.')[0]+'.fits',"readonly")
  nx=fitsobj[0].header['NAXIS1']
  ny=fitsobj[0].header['NAXIS2']
  aspect=float(ny)/nx
  hdr=fitsobj[0].header
  pix=fitsobj[0].data
  fitsobj.close()
  r1=sky+50.*skysig
  r2=sky-0.05*(r1-sky)

# guess for 1/3 total lum to set plot boundaries
  xlum=-2.5*math.log10((10.**(data[-1][1]/-2.5)/3.))
  for n in range(len(data)):
    if data[n][1] < xlum:
      mid=n
      break
  x=[] ; y=[]
  for tmp in data[mid:]:
    x.append(tmp[0])
    y.append(tmp[1])
  xmin=min(x)-0.10*(max(x)-min(x))
  ymin=min(y)-0.10*(max(y)-min(y))
  xmax=max(x)+0.10*(max(x)-min(x))
  ymax=max(y)+0.10*(max(y)-min(y))
  for n in range(mid): data[n][2]=1

# assign error bars to each mag
  up=[] ; down=[]
  for i in range(len(data)):
    up.append(-2.5*math.log10(10.**((data[i][1]-zpt)/-2.5)+(data[i][3]*skysig/(nsky**0.5)))+zpt)
    down.append(-2.5*math.log10(10.**((data[i][1]-zpt)/-2.5)-(data[i][3]*skysig/(nsky**0.5)))+zpt)

  for line in prf:
    if round(line[3],2) == round((10.**(data[imin][0]))/scale,2): break
  x0=data[imin][0]
  err=find_err()
  mag1,mag2,x1,x2,err1,err2,asym=plot()

  while 1:

    d=pgband(0)

    if d[2] == '?':
      print '/ = exit        b = change borders'
      print 'r = reset       a = adjust lum for better fit'
      print 'f = linear fit  x,1,2,3,4 = delete points'
      print 'z = set profile extrapolation point'
      print 'h = output hardcopy to tmp.ps'

    if d[2] == 'i':
      rmin=1.e33
      for t in data:
        r=abs(t[0]-d[0])
        if r < rmin:
          rmin=r
          emin=t[0]

    if d[2] == 'c':
      rold=r1
      k=d[0]*1.5/(xmax-xmin)+0.5-1.5*xmin/(xmax-xmin)
      r1=r1*k
      if r1 < sky: r1=(rold-sky)/2.+sky
      r2=sky-0.05*(r1-sky)

    if d[2] == 'z':
      rmin=1.e33
      for tmp in data:
        n=data.index(tmp)
        rr=abs(d[0]-tmp[0])
        if rr <= rmin:
          rmin=rr
          imin=n
      for n,tmp in enumerate(data[imin-2:]):
        data[n+imin-2][2]=0
      for line in prf:
        if round(line[3],2) == round((10.**(data[imin][0]))/scale,2): break

    if d[2] == 'q':
      sys.exit()

    if d[2] == '/':
#      file=open(sys.argv[-1].split('.')[0]+'.asym','w')
#      file.write('%5.2f' % (x1)+' '+'%9.5g' % (mag1)+' '+'%6.3g' % (err1))
#      file.write('\n')
#      file.write('%5.2f' % (x2)+' '+'%9.5g' % (mag2)+' '+'%6.3g' % (err2))
#      file.write('\n')
#      file.write('%9.5g' % (asym))
#      file.write('\n')
#      file.close()

      if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
#        doc = minidom.parse(sys.argv[1].split('.')[0]+'.xml')
#        rootNode = doc.documentElement
#        elements=xml_read(rootNode).walk(rootNode)
        out=xml_write(sys.argv[1].split('.')[0]+'.xml',rootNode.nodeName)
        for t in ['tot_rad_raw','tot_mag_raw','tot_mag_raw_err','tot_rad_exp', \
                  'tot_mag_exp','tot_mag_exp_err','tot_mag_asym']:
          try:
            del elements[t]
          except:
            pass
        out.loop(elements)

      else:
        out=xml_write(sys.argv[-1].split('.')[0]+'.xml','archangel')

      out.dump('  <tot_rad_raw units=\'log arcsecs\'>\n    '+'%.2f' % (x1)+'\n  </tot_rad_raw>\n')
      out.dump('  <tot_mag_raw units=\'mags\'>\n    '+'%.5g' % (mag1)+'\n  </tot_mag_raw>\n')
      out.dump('  <tot_mag_raw_err units=\'mags\'>\n    '+'%.3g' % (err1)+'\n  </tot_mag_raw_err>\n')
      out.dump('  <tot_rad_exp units=\'log arcsecs\'>\n    '+'%.2f' % (x2)+'\n  </tot_rad_exp>\n')
      out.dump('  <tot_mag_exp units=\'mags\'>\n    '+'%.5g' % (mag2)+'\n  </tot_mag_exp>\n')
      out.dump('  <tot_mag_exp_err units=\'mags\'>\n    '+'%.3g' % (err2)+'\n  </tot_mag_exp_err>\n')
      if str(asym) != 'nan': out.dump('  <tot_mag_asym units=\'mags\'>\n    '+'%.5g' % (asym)+'\n  </tot_mag_asym>\n')
      out.close()

      break

    if d[2] == 'b':
      xmin=float(d[0])
      ymax=float(d[1])
      d=pgband(0)
      xmax=float(d[0])
      ymin=float(d[1])

    if d[2] == 'r':
      x=[] ; y=[]
      for tmp in data:
        x.append(tmp[0])
        y.append(tmp[1])
      xmin=min(x)-0.10*(max(x)-min(x))
      ymin=min(y)-0.10*(max(y)-min(y))
      xmax=max(x)+0.10*(max(x)-min(x))
      ymax=max(y)+0.10*(max(y)-min(y))
      for n in range(len(data)): data[n][2]=0

    if d[2] in ['1','2','3','4','x']:
      rmin=1.e33
      for n,tmp in enumerate(data):
#        n=data.index(tmp)
        rr=((d[0]-tmp[0])**2+(d[1]-tmp[1])**2)**0.5
        if rr <= rmin:
          rmin=rr
          dmin=n
        if d[2] == '1' and tmp[0] > d[0] and tmp[1] < d[1]: data[n][2]=1
        if d[2] == '2' and tmp[0] < d[0] and tmp[1] < d[1]: data[n][2]=1
        if d[2] == '3' and tmp[0] < d[0] and tmp[1] > d[1]: data[n][2]=1
        if d[2] == '4' and tmp[0] > d[0] and tmp[1] > d[1]: data[n][2]=1
      if d[2] == 'x': data[dmin][2]=abs(data[dmin][2]-1)

    if d[2] == 'h':
      print 'dump hardcopy to tmp.ps'
      pgend()
      pgbeg('tmp.ps/vcps',1,1)
      pgask(0)
      pgscr(0,1.,1.,1.)
      pgscr(1,0.,0.,0.)
      pgscf(2)
      pgpap(8.0,1.0)
      mag1,mag2,x1,x2,err1,err2,asym=plot()
      pgend()
      pgbeg('/xs',1,1)
      pgask(0)
      pgscr(0,1.,1.,1.)
      pgscr(1,0.,0.,0.)
      pgscf(2)
      pgpap(10.0,1.0)
      mag1,mag2,x1,x2,err1,err2,asym=plot()

    mag1,mag2,x1,x2,err1,err2,asym=plot()
