#!/usr/bin/env python

import sys, os.path, pyfits, time, subprocess
from pylab import *
from matplotlib.ticker import MultipleLocator
from matfunc import *
from xml.dom import minidom, Node
from xml_archangel import *
from matplotlib.patches import Ellipse

def do_fit(x,lum):
  fit=array([x,lum])
  try:
    a,b,c=polyfit(fit,2)
  except:
    a=1. ; b=1. ; c=1.
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
    if tmp[2]:
      x.append(tmp[0])
      y.append(tmp[1])
  xlum=10.**((data[imin-1][1]-zpt)/-2.5)

  for tmp in data[imin:]:
    if tmp[2] and str(tmp[4]) != 'nan':
      xlum=xlum+10.**(tmp[4]/-2.5)
      x.append(tmp[0])
      y.append(-2.5*math.log10(xlum)+zpt)

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

  xmax=max(x)+0.10*(max(x)-xmin)
  if '-linear' in sys.argv:
    ymin=min(y)-0.20*(max(y)-min(y))
  else:
    ymin=min(y)-0.10*(max(y)-min(y))
  return xmax,ymin

def plot_asym():
  global axe,xmin,xmax,ymin,ymax,data,cmd,line,ft,cid1,cid2,imin,pix,r1,r2,prf,igray,trap
  global mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,iasym,sky,half,half_r,fit_max,fit_min,old_mag

  clf() ; axe = fig.add_subplot(111) ; asym=0.

  axis([xmin,xmax,ymax,ymin])
  xlabel('log r (arcsecs)')
  ylabel('$m_{app}$')
  suptitle(sys.argv[-1].split('.')[0])

#  ioff()

# mark start point for exp addition
  axe.scatter([data[imin][0]],[data[imin][1]],s=250,marker=(4,0,0),color='g')
  axe.scatter([data[imin][0]],[data[imin][1]],s=250,marker=(4,0,0),color='g')
  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymax,ymin)

# plot prf fitted datapoints, in blue, after start point, column 4
  x=[] ; lum=[] ; iplot=0
  for tmp in data[:imin+1]: # use raw up to start point
    if tmp[2]:
      iplot=iplot+1 # only plot blue circles after start point
      x.append(tmp[0])
      lum.append(tmp[1])
  if iplot < len(x)+1: iplot=1
  xlum=10.**((data[imin][1]-zpt)/-2.5)
  for tmp in data[imin+1:]:
    xlum=xlum+10.**(tmp[4]/-2.5)
    if tmp[0] > fit_max:
      x.append(tmp[0])
      lum.append(-2.5*math.log10(xlum)+zpt)
  axe.scatter(x,lum,s=75,marker='8',edgecolor='r',facecolor='w')
  x=[] ; lum=[]
  xlum=10.**((data[imin][1]-zpt)/-2.5)
  for tmp in data[imin+1:]:
    if str(tmp[4]) != 'nan' and tmp[0] <= fit_max:
      xlum=xlum+10.**(tmp[4]/-2.5)
      x.append(tmp[0])
      lum.append(-2.5*math.log10(xlum)+zpt)
#      print tmp[0],-2.5*math.log10(xlum)+zpt
  axe.scatter(x[iplot:],lum[iplot:],s=75,marker='8',edgecolor='b',facecolor='w')
  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymax,ymin)

#  print len(x),len(data),imin,fit_max,data[-1][1]

  if not iasym:
# plot fit, in blue
    z,a,b,c,x1,err1=do_fit(x,lum)
    mag1=a*x1**2+b*x1+c
    axe.plot(x,z,'b-')
# mark position of zero slope point
    figtext(0.15,0.85,'Polynomial fit',color='k',horizontalalignment='left',verticalalignment='center')
    text(x1,ymin+0.04*(ymax-ymin),'$\downarrow$',color='b',horizontalalignment='center',verticalalignment='center')
    text(xmax-0.04*(xmax-xmin),mag1,'$\leftarrow$',color='b',horizontalalignment='center',verticalalignment='center')
    err1=find_err()
    if old_mag:
      tmp='%6.3f' % (mag1)+' +/- '+'%6.3g' % (err1)+'  ('+'%6.3f' % (old_mag)+')'
    else:
      tmp='%6.3f' % (mag1)+' +/- '+'%6.3g' % err1
    figtext(0.15,0.79,'SFB:',color='b',horizontalalignment='left',verticalalignment='center')
    figtext(0.22,0.79,tmp,color='b',horizontalalignment='left',verticalalignment='center')

  else:
    pts=reshape(array(x+lum),(2,len(x)))
    try:
      if len(pts[0]) < 5: raise
      coeff=ratfit(pts)
    except:
      coeff=[1.,1.,1.,1.,1.]

# plot asym curve
    z,a,b,c,x1,err1=do_fit(x,lum)
    z=[]
    for tmp in x:
      z.append(rat_calc(tmp,coeff,2))
    axe.plot(x,z,'b-')
# using last point as asym mag
# math def is asym=coeff[0]/coeff[3]
    figtext(0.15,0.85,'Asymptotic fit',color='k',horizontalalignment='left',verticalalignment='center')
    text(xmax-0.04*(xmax-xmin),rat_calc(x[-1],coeff,2),'$\leftarrow$',color='b',horizontalalignment='center',verticalalignment='center')
    mag1=rat_calc(x[-1],coeff,2)
    if old_mag:
      tmp='%6.3f' % (mag1)+' +/- '+'%6.3g' % (err1)+'  ('+'%6.3f' % (old_mag)+')'
    else:
      tmp='%6.3f' % (mag1)+' +/- '+'%6.3g' % err1
    figtext(0.15,0.79,'SFB:',color='b',horizontalalignment='left',verticalalignment='center')
    figtext(0.22,0.79,tmp,color='b',horizontalalignment='left',verticalalignment='center')

  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymax,ymin)

# plot sfb fit datapoints, column 5
  x=[] ; lum=[] ; iplot=0
#  print imin,len(data),fit_max,data[-1][0]
  for tmp in data[:imin+1]:
#    if tmp[0] <= fit_max:
    if tmp[2] and tmp[0] <= fit_max:
      iplot=iplot+1
      x.append(tmp[0])
      lum.append(tmp[1])
  if iplot < len(x)+1: iplot=1
  xlum=10.**((data[imin][1]-zpt)/-2.5)
  for tmp in data[imin+1:]:
    if tmp[2] and tmp[0] <= fit_max:
#    if tmp[0] <= fit_max:
      xlum=xlum+10.**(tmp[5]/-2.5)
      x.append(tmp[0])
      lum.append(-2.5*math.log10(xlum)+zpt)
  axe.scatter(x[iplot:],lum[iplot:],s=75,marker='x',edgecolor='g',facecolor='w')
  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymax,ymin)

  if not iasym:
# plot fit to sfb fit data
    z,a,b,c,x2,err2=do_fit(x,lum)
    mag2=a*x2**2+b*x2+c
    axe.plot(x,z,'g-')
# mark position of zero slope point
    text(x2,ymin+0.04*(ymax-ymin),'$\downarrow$',color='g',horizontalalignment='center',verticalalignment='center')
    text(xmax-0.04*(xmax-xmin),mag2,'$\leftarrow$',color='g',horizontalalignment='center',verticalalignment='center')
    tmp='%6.3f' % (mag2)+' +/- '+'%6.3g' % err2
    figtext(0.15,0.76,'Fit:',color='g',horizontalalignment='left',verticalalignment='center')
    figtext(0.22,0.76,tmp,color='g',horizontalalignment='left',verticalalignment='center')

  else:
    pts=reshape(array(x+lum),(2,len(x)))
    try:
      if len(pts[0]) < 5: raise
      coeff=ratfit(pts)
    except:
      coeff=[1.,1.,1.,1.,1.]

# plot asym curve
    z,a,b,c,x2,err2=do_fit(x,lum)
    z=[]
    for tmp in x:
      z.append(rat_calc(tmp,coeff,2))
    axe.plot(x,z,'g-')
# using last point as asym mag
# math def is asym=coeff[0]/coeff[3]
    text(xmax-0.04*(xmax-xmin),rat_calc(x[-1],coeff,2),'$\leftarrow$',color='g',horizontalalignment='center',verticalalignment='center')
    mag2=rat_calc(x[-1],coeff,2)
    tmp='%6.3f' % (mag2)+' +/- '+'%6.3g' % err2
    figtext(0.15,0.76,'Fit:',color='g',horizontalalignment='left',verticalalignment='center')
    figtext(0.22,0.76,tmp,color='g',horizontalalignment='left',verticalalignment='center')

# plot raw photometry datapoints, plot last to be on top
  x=[] ; y=[] ; last=0. ; isw=0
  for tmp in data:
    if tmp[1] != tmp[1]: continue
    if not isw and tmp[1] >= last:
      isw=1
    if not tmp[2] or isw:
      x.append(tmp[0])
      y.append(tmp[1])
    last=tmp[1]
  axe.scatter(x,y,s=50,marker=(6,2,0),color='r')
  x=[] ; y=[] ; last=1.e33
  for tmp in data[1:]:
    if tmp[1] != tmp[1]: continue
#    if tmp[1] >= last: break
    if tmp[2]:
      x.append(tmp[0])
      y.append(tmp[1])
    last=tmp[1]
  axe.scatter(x,y,s=50,marker=(6,2,0),color='k')
  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymax,ymin)

  if not iasym:
    z,a,b,c,x3,err3=do_fit(x,y)
    mag3=a*x3**2+b*x3+c
    axe.plot(x,z,'k-')
    text(x3,ymin+0.04*(ymax-ymin),'$\downarrow$',color='k',horizontalalignment='center',verticalalignment='center')
    text(xmax-0.04*(xmax-xmin),mag3,'$\leftarrow$',color='k',horizontalalignment='center',verticalalignment='center')
    tmp='%6.3f' % (mag3)+' +/- '+'%6.3g' % err3
    figtext(0.15,0.82,'Raw:',color='k',horizontalalignment='left',verticalalignment='center')
    figtext(0.22,0.82,tmp,color='k',horizontalalignment='left',verticalalignment='center')

  else:
    pts=reshape(array(x+y),(2,len(x)))
    try:
      if len(pts[0]) < 5: raise
      coeff=ratfit(pts)
    except:
      coeff=[1.,1.,1.,1.,1.]

# plot asym curve
    z,a,b,c,x3,err3=do_fit(x,y)
    z=[]
    for tmp in x:
      z.append(rat_calc(tmp,coeff,2))
    axe.plot(x,z,'k-')
    text(xmax-0.04*(xmax-xmin),rat_calc(x[-1],coeff,2),'$\leftarrow$',color='k',horizontalalignment='center',verticalalignment='center')
    mag3=rat_calc(x[-1],coeff,2)
    tmp='%6.3f' % (mag3)+' +/- '+'%6.3g' % err3
    figtext(0.15,0.82,'Raw:',color='k',horizontalalignment='left',verticalalignment='center')
    figtext(0.22,0.82,tmp,color='k',horizontalalignment='left',verticalalignment='center')

  half=-2.5*log10(0.5*(10.**(mag1/-2.5)))
  last=data[0]
  for tmp in data[1:]:
    if tmp[1] < half:
      if '-linear' in sys.argv:
        half_r=(last[0]+(tmp[0]-last[0])*(half-last[1])/(tmp[1]-last[1]))
      else:
        half_r=10.**(last[0]+(tmp[0]-last[0])*(half-last[1])/(tmp[1]-last[1]))
      break
    last=tmp
  else:
    if '-linear' in sys.argv:
      half_r=data[-10][0]
    else:
      half_r=10.**data[-10][0]
  if '-linear' in sys.argv:
    axe.scatter([half_r],[half],s=250,marker=(4,0,0),color='m')
  else:
    axe.scatter([log10(half_r)],[half],s=250,marker=(4,0,0),color='m')

  axe.set_xlim(xmin,xmax)
  axe.set_ylim(ymax,ymin)

  if igray:
    try:
      a = axes([.5,.15,.35,.35])
      setp(a,xticks=[],yticks=[])
      gray()
      imshow(-pix,vmin=-r1,vmax=-r2,aspect='equal',origin='lower',interpolation='nearest')
      if '-linear' in sys.argv:
        test=round(((data[imin][0]))/scale,2)
      else:
        test=round((10.**(data[imin][0]))/scale,2)
      for t in prf:
        if round(t[3],2) == test:
          e=Ellipse((t[14],t[15]),2.*t[3],2.*t[3]*(1.-t[12]),t[13],fill=0)
          break
      e.set_clip_box(a.bbox)
      e.set_alpha(1.0)
      e.set_edgecolor('g')
      a.add_artist(e)
    except:
      pass

#  ion()
  draw()
  if '-hard' in sys.argv:
    fig.savefig('asym.pdf')
    sys.exit()

  return mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,half,half_r

def find_err():
  global x0,up,down,zpt,scale
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

def get_data(isky):
  global axe,xmin,xmax,ymin,ymax,data,cmd,line,ft,cid1,cid2,imin,pix,r1,r2,prf,igray,trap
  global mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,iasym,sky,half,half_r,fit_max,fit_min,old_mag
  global x0,up,down,zpt,scale

  if os.path.exists(sys.argv[-1].split('.')[0]+'.xml'):
    name=sys.argv[-1]
    root='.'
  else:
    try:
      for root, dirs, files in os.walk('.'):
        for name in files:
          if 'xml' not in name: continue
          if sys.argv[-1] in name:
            raise
      else:
        print file,'no file found'
        sys.exit()
    except:
      pass

  try:
    doc = minidom.parse(root+'/'+name.split('.')[0]+'.xml')
    rootNode = doc.documentElement
    elements=xml_read(rootNode).walk(rootNode)

    if isky:
      try:
        sky=float(elements['sky'][0][1])
      except:
        print 'sky value not found, setting to zero'
        sky=0.

    try:
      old_mag=float(elements['tot_mag_sfb'][0][1])
    except:
      old_mag=None

    try:
      skysig=float(elements['skysig'][0][1])
    except:
      print 'skysig not found, setting to one'
      skysig=1.

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
      exptime=float(elements['exptime'][0][1])
    except:
      exptime=1.
    if exptime != 0.:
      try:
        k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05}
        airmass=k[elements['filter'][0][1]]*float(elements['airmass'][0][1])
      except:
        airmass=0.
      zpt=2.5*math.log10(exptime)-airmass+zpt

    try:
      for t in elements['array']:
        if t[0]['name'] == 'prf':
          prf=[]
          for z in t[2]['axis']:
            prf.append(map(float,z[1].split('\n')))
          tmp=array(prf)
          prf=swapaxes(tmp,1,0)
          break
      else:
        print 'no prf data in .xml file - aborting'
        sys.exit()
    except:
      raise
      print 'problem with data in .xml file - aborting'
      sys.exit()

    for istop,z in enumerate(prf):
#      if z[0]-sky < (prf[0][0]-sky)/5.: break
#      if z[0]-sky < (prf[0][0]-sky)/1.2: break
      if z[0]-sky < (prf[0][0]-sky)/3.: break
    xstop=z[3]
#    print 'xstop',xstop,istop

    iasym=1
    try:
      if elements['tot_mag_iter_pt'][0][0] == 'polynomical fit': iasym=0
    except:
      pass
#    print 'iasym',iasym,prf[0][0]-sky,len(prf)

    try:
      for t in elements['array']:
        if t[0]['name'] == 'ept':
          pts=[]
          for z in t[2]['axis']:
            pts.append(map(float,z[1].split('\n')))
          tmp=array(pts)
          pts=swapaxes(tmp,1,0)
          break
      else:
        print 'no ept data in .xml file - aborting'
        sys.exit()
    except:
      raise
      print 'problem with data in .xml file - aborting'
      sys.exit()

    try:
      for imin,z in enumerate(pts):
        if round(scale*z[0],2) >= float(elements['tot_mag_iter_pt'][0][1]):
          xmn=round(scale*z[0],2)
          break
#      print imin,xmn,float(elements['tot_mag_iter_pt'][0][1])
#      raise
    except:
      for imin,z in enumerate(prf):
#        if z[0]-sky < (prf[0][0]-sky)/20.: break
#        print z[3],z[0]-sky,(prf[0][0]-sky)/100
        if z[0]-sky < (prf[0][0]-sky)/100.: break
      xmn=round(z[3],2)
#      print imin,xmn

#    print xmn,istop,imin

    data=[]
# storing log r (arcsecs), app mag, erase flag, number of pixels (for
# error), prf intensity, exp intensity

    for n,line in enumerate(pts):
      if round(line[0],2) == xstop: istop=n
      if line[0] < xstop or int(line[-1]) == 0:
        erase=0
      else:
        erase=1
      if '-linear' in sys.argv:
        t=scale*line[0]
      else:
        t=math.log10(scale*line[0])
      data.append([t,
                   line[1]+zpt,
                   erase,
                   line[2],
                   line[3],
                   line[4]])
      if round(line[0],2) == xmn: imin=n
#    print 'data',istop,imin,len(data),xmn

#    print xmn,istop,imin
    if imin > len(data)-5: imin=max(1,len(data)-5)

  except:
    print 'no .xml file'
    sys.exit()

  try:
    fit_min=log10(float(elements['tot_mag_fit_lower'][0][1]))
    fit_max=log10(float(elements['tot_mag_fit_upper'][0][1]))
    for n,tmp in enumerate(data):
      if tmp[0] >= fit_min and tmp[0] <= fit_max:
        data[n][2]=1
      else:
        data[n][2]=0

  except:
    pass

  if os.path.exists(root+'/'+name.split('.')[0]+'.fits') or \
     os.path.exists(root+'/'+name.split('.')[0]+'.raw'):
    igray=1
  else:
    igray=0

  if igray:
    if '.' not in sys.argv[-1] or sys.argv[-1].split('.')[1] == '':
      try:
        fitsobj=pyfits.open(root+'/'+name.split('.')[0]+'.fits',"readonly")
      except:
        fitsobj=pyfits.open(root+'/'+name.split('.')[0]+'.raw',"readonly")
    else:
      fitsobj=pyfits.open(root+'/'+name,"readonly")
    nx=fitsobj[0].header['NAXIS1']
    ny=fitsobj[0].header['NAXIS2']
    aspect=float(ny)/nx
    hdr=fitsobj[0].header
    pix=fitsobj[0].data
    fitsobj.close()
    r1=sky+50.*skysig
    r2=sky-0.05*(r1-sky)

# guess for 1/5 total lum to set plot boundaries
#  xlum=-2.5*math.log10((10.**(data[-1][1]/-2.5)/5))
#  for n in range(len(data)):
#    if data[n][1] < xlum:
#      mid=n
#      break
  x=[] ; y=[]
  for tmp in data[max(1,istop-5):]:
    x.append(tmp[0])
    y.append(tmp[1])
  xmin=min(x)-0.10*(max(x)-min(x))
  if '-linear' in sys.argv:
    ymin=min(y)-0.20*(max(y)-min(y))
  else:
    ymin=min(y)-0.10*(max(y)-min(y))
  xmax=max(x)+0.10*(max(x)-min(x))
  ymax=max(y)+0.10*(max(y)-min(y))

#  for n in range(istop):
#    data[n][2]=0

  try:
    fit_min
  except:
    fit_min=data[istop][0]
    fit_max=data[-3][0]

# assign error bars to each mag
  up=[] ; down=[]
  for i in range(len(data)):
    try:
      up.append(-2.5*math.log10(10.**((data[i][1]-zpt)/-2.5)+(data[i][3]*skysig))+zpt)
      lastx=-2.5*math.log10(10.**((data[i][1]-zpt)/-2.5)+(data[i][3]*skysig))+zpt
    except:
      up.append(lastx)
    try:
      down.append(-2.5*math.log10(10.**((data[i][1]-zpt)/-2.5)-(data[i][3]*skysig))+zpt)
      lasty=-2.5*math.log10(10.**((data[i][1]-zpt)/-2.5)-(data[i][3]*skysig))+zpt
    except:
      down.append(lasty)

  if '-linear' in sys.argv:
    test=data[imin][0]/scale
  else:
    test=10.**(data[imin][0])/scale
  for line in prf:
    if round(line[3],2) == round(test,2): break
  x0=data[imin][0]
  err=find_err()

  return

def action(): # do the actions from clicker as given by var cmd
  global axe,xmin,xmax,ymin,ymax,data,cmd,line,ft,cid1,cid2,imin,pix,r1,r2,prf,igray,trap
  global mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,iasym,sky,half,half_r,fit_max,fit_min,old_mag

  try:
    if cmd == 'b': # do borders
      xmin=float(line.split(': ')[-1].split()[0])
      xmax=float(line.split(': ')[-1].split()[1])
      if float(line.split(': ')[-1].split()[2]) > float(line.split(': ')[-1].split()[3]):
        ymax=float(line.split(': ')[-1].split()[2])
        ymin=float(line.split(': ')[-1].split()[3])
      else:
        ymin=float(line.split(': ')[-1].split()[2])
        ymax=float(line.split(': ')[-1].split()[3])
    if cmd == 's': # new sky
      sky=float(line.split(': ')[-1])
      if os.path.exists(sys.argv[-1].split('.')[0]+'.fake'):
        os.system('el -fit -sky '+str(sky)+' '+sys.argv[-1].split('.')[0]+'.fake')
      elif os.path.exists(sys.argv[-1].split('.')[0]+'.clean'):
        os.system('el -fit -sky '+str(sky)+' '+sys.argv[-1].split('.')[0]+'.clean')
      else:
        os.system('el -fit -sky '+str(sky)+' '+sys.argv[-1].split('.')[0]+'.fits')
      get_data(0)
  except:
    fig.texts.remove(ft)
    ft=figtext(0.1,0.05,'INPUT ERROR',horizontalalignment='left',verticalalignment='top',color='r')
    time.sleep(2)

  fig.texts.remove(ft)
  line=''

  mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,half,half_r=plot_asym()
  return

def clicker(event):
  global axe,xmin,xmax,ymin,ymax,data,cmd,line,ft,cid1,cid2,imin,pix,r1,r2,prf,igray,trap
  global mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,iasym,sky,half,half_r,fit_max,fit_min,old_mag

  if event.key in ['b','s'] or trap:
    if not trap:
      if event.key == 'b':
        line='Enter borders: '
        cmd='b'
      if event.key == 's':
        line='Enter sky: '
        cmd='s'
      trap=1
    else:
      if event.key == 'enter':
        action()
        trap=0
      elif event.key == 'backspace': # delete characters, stop at 0 or ': '
        try:
          if line[-2:] != ': ': line=line[:-1]
        except:
          pass
      elif event.key in [None,'shift','control','alt','right','left','up','down','escape'] or ord(event.key) == 0:
        pass
      else:
        line=line+event.key

    try:
      fig.texts.remove(ft) # remove the line for redraw
    except:
      pass
    ft=figtext(0.1,0.05,line,horizontalalignment='left',verticalalignment='top')
    draw()

  else:

    cmd=event.key

    if event.key == 'q':
      disconnect(cid1)
      close('all')
      time.sleep(0.5)
      sys.exit()

    if event.key == 'h':
      fig.set_size_inches((8,8))
      mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,half,half_r=plot_asym()
      fig.savefig('asym.pdf')

    if event.key in ['Z','X','/']:
      if not iasym:
        units='polynomical fit'
      else:
        units='asymptotic fit'
      if event.key == 'Z':
        os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_quality fair')
      if event.key == 'X':
        os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_quality poor')
      if event.key == '/':
        os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_quality ok')
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_rad_raw units=\''+units+'\' '+'%.2f' % (10.**x3))
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_raw units=\''+units+'\' '+'%.5f' % mag3)
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_raw_err units=\''+units+'\' '+'%.3f' % err3)
      if '-linear' in sys.argv:
        os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_rad_sfb units=\''+units+'\' '+'%.2f' % (x1))
      else:
        os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_rad_sfb units=\''+units+'\' '+'%.2f' % (10.**x1))
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_sfb units=\''+units+'\' '+'%.5f' % mag1)
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_sfb_err units=\''+units+'\' '+'%.3f' % err1)
      if '-linear' in sys.argv:
        os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_rad_fit units=\''+units+'\' '+'%.2f' % (x1))
      else:
        os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_rad_fit units=\''+units+'\' '+'%.2f' % (10.**x1))
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_fit units=\''+units+'\' '+'%.5f' % mag2)
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_fit_err units=\''+units+'\' '+'%.3f' % err2)
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_raw_last units=\''+units+'\' '+'%.3f' % data[-1][1])
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_sky units=\''+units+'\' '+'%.3f' % sky)
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_half_lum units=\''+units+'\' '+'%.5f' % half)
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_half_rad units=\'arcsecs\' '+'%.2f' % half_r)
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_fit_lower units=\'arcsecs\' '+'%.2f' % 10.**(fit_min))
      os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_fit_upper units=\'arcsecs\' '+'%.2f' % 10.**(fit_max))
      if '-linear' in sys.argv:
        os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_iter_pt units=\'arcsecs\' '+'%.2f' % (data[imin][0]))
      else:
        os.system('xml_archangel -e '+sys.argv[-1].split('.')[0]+' tot_mag_iter_pt units=\'arcsecs\' '+'%.2f' % 10.**(data[imin][0]))

# redo sky and write out new ept
#    p=subprocess.Popen('xml_archangel -a '+sys.argv[-1].split('.')[0]+' ept', \
#                        shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
#    lines='radius         mag             area           xsfb            expm            kill\n'
#    for z in data:
#      if '-linear' in sys.argv:
#        lines=lines+'%16.8e' % ((z[0])/scale)
#      else:
#        lines=lines+'%16.8e' % ((10.**z[0])/scale)
#      lines=lines+'%16.8e' % (z[1]-zpt)
#      lines=lines+'%16.8e' % z[3]
#      lines=lines+'%16.8e' % z[4]
#      lines=lines+'%16.8e' % z[5]
#      lines=lines+' '+str(z[2])
#      lines=lines+'\n'
#    p.communicate(lines[:-1])

      disconnect(cid1)
      close('all')
      time.sleep(0.5)
      sys.exit()

    if event.key == 'a':
      iasym=abs(iasym-1)

#  if event.key == 'i' and igray:
#    rmin=1.e33
#    for t in data:
#      r=abs(t[0]-event.xdata)
#      if r < rmin:
#        rmin=r
#        emin=t[0]

    if event.key == 'c' and igray:
      rold=r1
      k=event.xdata*1.5/(xmax-xmin)+0.5-1.5*xmin/(xmax-xmin)
      r1=r1*k
      if r1 < sky: r1=(rold-sky)/2.+sky
      r2=sky-0.05*(r1-sky)

# set the iter point (z-point), where the sfb and fit are started
    if event.key == 'z':
      rmin=1.e33
      for tmp in data:
        n=data.index(tmp)
        try:
          rr=abs(event.xdata-tmp[0])
          if rr <= rmin:
            rmin=rr
            imin=n
        except:
          break
#    for n,tmp in enumerate(data[imin-2:]):
#      data[n+imin-2][2]=1
#    for line in prf:
#      if round(line[3],2) == round((10.**(data[imin][0]))/scale,2): break

    if event.key == 'r':
      for tmp in data[max(1,istop-5):]:
        x.append(tmp[0])
        y.append(tmp[1])
      xmin=min(x)-0.10*(max(x)-min(x))
      if '-linear' in sys.argv:
        ymin=min(y)-0.20*(max(y)-min(y))
      else:
        ymin=min(y)-0.10*(max(y)-min(y))
      xmax=max(x)+0.10*(max(x)-min(x))
      ymax=max(y)+0.10*(max(y)-min(y))

    if event.key in ['1','2','3','4','x',',','.']:
      if event.key == '.': fit_max=event.xdata
      if event.key == ',': fit_min=event.xdata
      if event.key in ['.',',']:
        for n,tmp in enumerate(data):
          if tmp[0] >= fit_min and tmp[0] <= fit_max:
            data[n][2]=1
          else:
            data[n][2]=0
      else:
        rmin=1.e33
        for n,tmp in enumerate(data):
          rr=(((event.xdata-tmp[0])/(xmax-xmin))**2+((event.ydata-tmp[1])/(ymax-ymin))**2)**0.5
          if rr <= rmin:
            rmin=rr
            dmin=n
          if cmd == '1' and tmp[0] > event.xdata and tmp[1] > event.ydata: data[n][2]=abs(data[n][2]-1)
          if cmd == '2' and tmp[0] < event.xdata and tmp[1] > event.ydata: data[n][2]=abs(data[n][2]-1)
          if cmd == '3' and tmp[0] < event.xdata and tmp[1] < event.ydata: data[n][2]=abs(data[n][2]-1)
          if cmd == '4' and tmp[0] > event.xdata and tmp[1] < event.ydata: data[n][2]=abs(data[n][2]-1)
        if cmd == 'x': data[dmin][2]=abs(data[dmin][2]-1)

    mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,half,half_r=plot_asym()

# main

if '-h' in sys.argv:
  print 'Usage: asymptotic op xml_file'
  print
  print 'simply GUI that determines asymptotic fit on integrated galaxy mag,'
  print 'delivers mag/errors from apertures and curve of growth fit into XML file'
  print 'needs sfb, prf, ept output'
  print
  print 'options: -linear = use linear x-axis'
  print '         -hard = produce hardcopy'
  print
  print 'cursor commands:'
  print
  print 'r = reset                  z = set profile extrapolation point'
  print 's = enter manual sky       a = flip asym/poly fit'
  print
  print 'x,1,2,3,4 = delete points'
  print ', = kill below             . = kill above'
  print
  print 'c = greyscale control      b = change borders'
  print 'q = abort exit (no write)  / = exit'
  print 'Z = write fit, flag as tot_mag_quality = fair'
  print 'X = write fit, flag as tot_mag_quality = poor'
  sys.exit()

get_data(1)

geo=eval(' '.join([tmp[:-1] for tmp in open(os.environ['ARCHANGEL_HOME']+'/.archangel','r').readlines()]))
if 'prometheus' in os.uname()[1]:
  fig = figure(figsize=(12, 12), dpi=80)  # initialize plot parameters
  axe = fig.add_subplot(111)  # assign axe for text and axes
  manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
  manager.window.title('')
  manager.window.geometry('+1200+300') # move the window for deepcore big screen
else:
  fig = figure(figsize=(9, 9), dpi=80)  # initialize plot parameters
  axe = fig.add_subplot(111)  # assign axe for text and axes
  manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
  manager.window.title('')
#  manager.window.geometry('+400+50')
  manager.window.geometry(geo['main_window'])

xmax,ymin=min_max()
line='' ; cmd='' ; trap=0

mag1,mag2,mag3,x1,x2,x3,err1,err2,err3,half,half_r=plot_asym()

cid1=connect('key_press_event',clicker)
show()
