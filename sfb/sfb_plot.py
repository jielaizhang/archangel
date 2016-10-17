#!/usr/bin/env python

import sys, os.path, time, subprocess
import astropy.io.fits as pyfits
from math import *
from xml_archangel import *
from pylab import *
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Ellipse

def linfit(fit):
  sum=0.0
  sumx=0.0
  sumy=0.0
  sumxy=0.0
  sumx2=0.0
  sumy2=0.0
  n=0
  for tmp in fit:
    n+=1
    sum=sum+(1./tmp[2]**2)
    sumx=sumx+(1./tmp[2]**2)*tmp[0]
    sumy=sumy+(1./tmp[2]**2)*tmp[1]
    sumxy=sumxy+(1./tmp[2]**2)*tmp[0]*tmp[1]
    sumx2=sumx2+(1./tmp[2]**2)*tmp[0]*tmp[0]
    sumy2=sumy2+(1./tmp[2]**2)*tmp[1]*tmp[1]
  dex=sum*sumx2-sumx*sumx
# y intersect -- a
  a=(sumx2*sumy-sumx*sumxy)/dex
# slope -- b
  b=(sum*sumxy-sumx*sumy)/dex
# varience
  var=(sumy2+a*a*sum+b*b*sumx2-2.*(a*sumy+b*sumxy-a*b*sumx))/(n-2)
# correlation coefficient -- r
  r=(sum*sumxy-sumx*sumy)/((dex*(sum*sumy2-sumy*sumy))**0.5)
# sigma b
  sigb=(var*sumx2/dex)**0.5
# sigma m
  sigm=(var*sum/dex)**0.5
  sig=0.
  for tmp in fit:
    z=a+b*tmp[0]
    sig=sig+(z-tmp[1])**2
  sig=(sig/(n-1))**.5
  return a,b,r,sigb,sigm,sig

def plot_bdd(interactive):
  global ax,isfb,data,xmin,xmax,ymin,ymax,sky,skysig,pix,r1,r2,middle,prf,emin,s1,s2,fig,inner_fit,outer_fit,central_mu
  global x1,x2,cstore,sstore,cstore_c,sstore_c,xc,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic 
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge,xxstep,i1,i2,j1,j2,nx,ny

  r=[] ; s=[] ; v=[] ; w=[] ; e=[]
  for t in data:
    if ifit in [0,2,5]:
      for y in prf:
        if y[3] >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          break
    else:
      tmp=t[0]
    if t[2]:
      if ifit == 2:
        r.append(tmp**0.25)
      elif ifit == 0:
        r.append(log10(tmp))
      elif ifit == 5:
        r.append(log10(tmp))
      else:
        r.append(t[0])
      s.append(t[1])
      e.append(t[3])
    else:
      if ifit == 2:
        v.append(tmp**0.25)
      elif ifit == 0:
        v.append(log10(tmp))
      elif ifit == 5:
        v.append(log10(tmp))
      else:
        v.append(t[0])
      w.append(t[1])

#  ioff()
  axis([xmin,xmax,ymax,ymin])
  if ifit == 2:
    xlabel('r$^{1/4}$ (arcsecs)')
  elif ifit == 0:
    xlabel('log r (arcsecs)')
  elif ifit == 5:
    xlabel('log r (arcsecs)')
  else:
    xlabel('r (arcsecs)')
  ylabel('$\\mu$ (mag/arcsec$^{-2}$)')
  suptitle(sys.argv[-1].split('_')[0])

  try:
    for t in data:
      for y in prf:
        if y[3] >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          break
      if round(t[0],2) == round(emin,2):
        if ifit == 2:
          ax.scatter([tmp**0.25],[t[1]],s=100,marker='o',color='g',facecolor='w')
        elif ifit == 0:
          ax.scatter([log10(tmp)],[t[1]],s=100,marker='o',color='g',facecolor='w')
        elif ifit == 5:
          ax.scatter([log10(tmp)],[t[1]],s=100,marker='o',color='g',facecolor='w')
        else:
          ax.scatter([t[0]],[t[1]],s=100,marker='o',color='g',facecolor='w')
        break
  except:
    pass

# facecolor to give open symbols
#  for x,y in zip(r,s): print x,y
#  ax.scatter(r,s,s=75,marker=(4,0,0),facecolor=(1,1,1,0),color='k')
  ax.scatter(r,s,s=75,marker=(4,0,0),facecolor='w',color='k')
  ax.set_xlim(xmin,xmax)
  ax.set_ylim(ymax,ymin)

  n=0
  for x,y,err in zip(r,s,e):
    n+=1
    if err > abs(ymax-ymin)/200. and err > .1: errorbar(x,y,yerr=err,ecolor='k')

  draw_fit()
  fit=[]
  for x,y in zip(r,s):
    if x >= inner_fit and x <= outer_fit:
      fit.append([x,y,1.])
  a,b,rc,sigb,sigm,sig=linfit(fit)
  central_mu=a
#  ax.plot([xmin/2.,outer_fit],[a+b*(xmin/2.),a+b*outer_fit],'r--')
  ax.set_xlim(xmin,xmax)
  ax.set_ylim(ymax,ymin)

  if grey:
    a = axes([.50,.50,.35,.35])
    ticklabels = a.get_xticklabels()
    for label in ticklabels:
      label.set_fontsize(9)
    ticklabels = a.get_yticklabels()
    for label in ticklabels:
      label.set_fontsize(9)
    gray()
    zm=ma.masked_where(isnan(pix[j1-1:j2,i1-1:i2]), pix[j1-1:j2,i1-1:i2])
    imshow(-zm,vmin=-r1,vmax=-r2,extent=(i1-0.5,i2+0.5,j1-0.5,j2+0.5), \
           aspect='equal',origin='lower',interpolation='nearest')
    try:
      for t in prf:
        if round(t[3],2) == round(emin,2):
          e=Ellipse((t[14],t[15]),2.*t[3],2.*t[3]*(1.-t[12]),t[13],fill=0)
          break
      e.set_clip_box(a.bbox)
      e.set_alpha(1.0)
      e.set_edgecolor('g')
      a.add_artist(e)
    except:
      pass

  draw()
#    ion()

  if '-i' in sys.argv:
    fig.savefig(sys.argv[-1]+'_sfbplot.pdf')
    sys.exit()

def draw_fit():
  global ax,isfb,data,xmin,xmax,ymin,ymax,sky,skysig,pix,r1,r2,middle,prf,emin,s1,s2,fig,inner_fit,outer_fit,central_mu
  global x1,x2,cstore,sstore,cstore_c,sstore_c,xc,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic 
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge,xxstep,i1,i2,j1,j2,nx,ny

  try:
    yd=(ymax-ymin)/20.
    xd=(xmax-xmin)/20.
    xstep=xmax/300.

    axis([xmin,xmax,ymax,ymin])

    if ifit == 2:
      try:
        t1=[] ; t2=[]
        b=1.9992*n_sersic-0.3271
        for i in range(301):
          t=i*xstep+xmin+xd
          t1.append((10.**t)**(1./4.))
          t2.append(se_sersic+(2.5*b)*((10.**t/re_sersic)**(1./n_sersic)-1.)/log(10.))
        ax.plot(t1,t2,'b--')
      except:
        pass
      text(xmin+1.1*xd,ymin+1.3*yd,'de Vaucouleur r$^{1/4}$',color='b')
      ax.plot([xmin,xmax],[se_dev+8.325*((xmin**4./re_dev)**0.25-1.),se_dev+8.325*((xmax**4./re_dev)**0.25-1.)],'b-')
      text(xmin+xd,ymax-5.*yd,'$\\mu_e$ = '+('%5.2f' % se_dev))
      text(xmin+xd,ymax-4.*yd,'$r_e$ = '+('%5.2f' % re_dev))
      try:
        text(xmin+xd,ymax-1.*yd,'$\\chi^2$ = '+('%8.2e' % chisq_dev))
      except:
        pass
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymax,ymin)

    if ifit in [1,3,4,6]:
#      if ifit == 1:
#        text(xmin+xd,ymin+yd,'Disk',color='b')
#        try:
#          text(xmin+xd,ymax-1.*yd,'$\\chi^2$ = '+('%8.2e' % chisq_disk))
#        except:
#          pass
#      text(xmin+2*xd,ymin+1.2*yd,'Bulge+Disk',color='b')
      ax.plot([0.,xmax],[cstore,cstore+sstore*xmax],'b-')
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymax,ymin)
      text(xmin+xd,ymax-3.*yd,'$\\mu_o$ = '+('%5.2f' % cstore))
      alpha = 1.0857/sstore
      text(xmin+xd,ymax-2.*yd,'$\\alpha$ = '+('%5.2f' % alpha))
      if ifit == 6:
        ax.plot([0.,xc+0.5*xc],[cstore_c,cstore_c+sstore_c*(xc+0.5*xc)],'r-')
        ax.set_xlim(xmin,xmax)
        ax.set_ylim(ymax,ymin)

      if ifit in [3,4]:
        t1=[] ; t2=[]
        for i in range(301):
          t=i*xstep
          xnt=se_bulge+8.325*((t/re_bulge)**0.25-1.)
          xnt=-0.4*xnt
          xnt1=10.**xnt
          t1.append(t)
          t2.append(-2.5*log10(xnt1))
        ax.plot(t1,t2,'b--')
        ax.set_xlim(xmin,xmax)
        ax.set_ylim(ymax,ymin)

        t1=[] ; t2=[]
        for i in range(301):
          t=i*xstep
          xnt=se_bulge+8.325*((t/re_bulge)**0.25-1.)
          xnt=-0.4*xnt
          xnt1=10.**xnt
          xnt=cstore+sstore*t
          xnt=-0.4*xnt
          xnt2=10.**(xnt)
          xnt3=xnt1+xnt2
          t1.append(t)
          t2.append(-2.5*log10(xnt3))
        ax.plot(t1,t2,'b-')
        ax.set_xlim(xmin,xmax)
        ax.set_ylim(ymax,ymin)
        text(xmin+xd,ymax-5.*yd,'$\\mu_e$ = '+('%5.2f' % se_bulge))
        text(xmin+xd,ymax-4.*yd,'$r_e$ = '+('%5.2f' % re_bulge))
        try:
          text(xmin+xd,ymax-1.*yd,'$\\chi^2$ = '+('%8.2e' % chisq_bulge))
        except:
          pass
#        if ifit == 3:
#          text(xmin+xd,ymin+yd,'3P Bulge+Disk',color='b')
#        else:
#          text(xmin+xd,ymin+yd,'4P Bulge+Disk',color='b')

      xbm = se_bulge - 5.*log10(re_bulge) - 40.0
      alpha = 1.0857/sstore
      xdm = cstore - 5.*log10(alpha) - 38.6
      bdratio = 10.**(-0.4*(xbm - xdm))

    if ifit == 5:
#      text(xmin+xd,ymin+yd,'Sersic',color='b')
      t1=[] ; t2=[]
      b=1.9992*n_sersic-0.3271
      for i in range(301):
        t=i*xstep+xmin+xd
        t1.append(t)
        t2.append(se_sersic+(2.5*b)*((10.**t/re_sersic)**(1./n_sersic)-1.)/log(10.))
      text(xmin+2*xd,ymin+1.2*yd,'Sersic',color='b')
      ax.plot(t1,t2,'b-')
      text(xmin+xd,ymax-5.*yd,'$\\mu_e$ = '+('%5.2f' % se_sersic))
      text(xmin+xd,ymax-4.*yd,'$r_e$ = '+('%5.2f' % re_sersic))
      text(xmin+xd,ymax-3.*yd,'$n$ = '+('%5.2f' % n_sersic))
      try:
        text(xmin+xd,ymax-1.*yd,'$\\chi^2$ = '+('%8.2e' % chisq_sersic))
      except:
        pass
      try:
        t1=[] ; t2=[]
        for i in range(301):
          t=i*xstep+xmin+xd
          xnt=se_dev+8.325*((10.**t/re_dev)**0.25-1.)
          xnt=-0.4*xnt
          xnt1=10.**xnt
          t1.append(t)
          t2.append(-2.5*log10(xnt1))
        ax.plot(t1,t2,'b--')
      except:
        pass
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymax,ymin)

    if ifit == 0:
      t1=[] ; t2=[]
      b=1.9992*n_sersic-0.3271
      for i in range(301):
        t=i*xstep+xmin+xd
        t1.append(t)
        t2.append(se_sersic+(2.5*b)*((10.**t/re_sersic)**(1./n_sersic)-1.)/log(10.))
#        print t, se_sersic+(2.5*b)*((10.**t/re_sersic)**(1./n_sersic)-1.)/log(10.)
      ax.plot(t1,t2,'r-')
      try:
        t1=[] ; t2=[]
        for i in range(301):
          t=i*xstep+xmin+xd
          xnt=se_dev+8.325*((10.**t/re_dev)**0.25-1.)
          xnt=-0.4*xnt
          xnt1=10.**xnt
          t1.append(t)
          t2.append(-2.5*log10(xnt1))
        ax.plot(t1,t2,'b-')
      except:
        pass
      try:
        t1=[] ; t2=[]
        for i in range(301):
          tmp=i*xstep+xmin+xd
          for y in prf:
            if y[3] >= 10.**tmp:
              xx=10.**tmp
              t=(xx*xx/(1.-y[12]))**0.5
              break
          else:
            xx=10.**tmp
            t=(xx*xx/(1.-prf[-1][12]))**0.5
          xnt=se_bulge+8.325*((t/re_bulge)**0.25-1.)
          xnt=-0.4*xnt
          xnt1=10.**xnt
          xnt=cstore+sstore*t
          xnt=-0.4*xnt
          xnt2=10.**(xnt)
          xnt3=xnt1+xnt2
          t1.append(tmp)
          t2.append(-2.5*log10(xnt3))
        ax.plot(t1,t2,'g-')
      except:
        pass
      ax.plot([xmin+xd,xmin+2*xd],[ymax-5.*yd,ymax-5.*yd],'r-')
      text(xmin+2.3*xd,ymax-5.*yd,'- Sersic',verticalalignment='center')
      ax.plot([xmin+xd,xmin+2*xd],[ymax-4.*yd,ymax-4.*yd],'b-')
      text(xmin+2.3*xd,ymax-4.*yd,'- r$^{1/4}$',verticalalignment='center')
      ax.plot([xmin+xd,xmin+2*xd],[ymax-3.*yd,ymax-3.*yd],'g-')
      text(xmin+2.3*xd,ymax-3.*yd,'- bulge+disk',verticalalignment='center')
      ax.set_xlim(xmin,xmax)
      ax.set_ylim(ymax,ymin)

  except:
    pass

def help():
  return '''
Usage: sfb_plot options file_name

surface photometry plot, output to file_name_sfbplot.pdf

options: -h = this message
         -c = show central sfb fit
         -d = show disk fit
         -e = show r^1/4 fit
         -s = show Sersic fit
         -i = no interactive
         -r = use raw FITS frame

q = abort              / = exit and output hardcopy'''

def clicker(event):
  global ax,isfb,data,xmin,xmax,ymin,ymax,sky,skysig,pix,r1,r2,middle,prf,emin,s1,s2,fig,inner_fit,outer_fit,central_mu
  global x1,x2,cstore,sstore,cstore_c,sstore_c,xc,re_bulge,se_bulge,re_dev,se_dev,re_sersic,se_sersic,n_sersic,ifit
  global lower_fit_disk,lower_fit_dev,lower_fit_sersic,upper_fit_disk,upper_fit_dev,upper_fit_sersic 
  global chisq_disk,chisq_dev,chisq_sersic,chisq_bulge,xxstep,i1,i2,j1,j2,nx,ny

# ifit = 1, disk only fit
#      = 2, r^1/4 only fit
#      = 3, B+D fit, hold central disk sfb
#      = 4, B+D fit, all four parameters
#      = 5, Sersic fit

  if event.key == 'q':
    disconnect(cid)
    close('all')
    time.sleep(0.5)
    sys.exit()

  if event.key == '/':
#    ioff()
    fig = figure(figsize=(8, 8), dpi=80)
    clf()
    ax = fig.add_subplot(111)
    plot_bdd(False)
    savefig(sys.argv[-1]+'_sfbplot.pdf')
    disconnect(cid)
#    os.system('xml_archangel -e '+sys.argv[ifile]+' sfb_plot_contrast "'+ \
#                       str(r1)+' '+str(middle)+' '+str(r2)+'"')
#    os.system('xml_archangel -e '+sys.argv[ifile]+' sfb_plot_zoom "'+ \
#                       str(i1)+' '+str(i2)+' '+str(j1)+' '+str(j2)+' '+str(xxstep)+'"')
    os.system('xml_archangel -e '+sys.argv[-1]+' sfb_plot_borders "'+ \
                       str(xmin)+' '+str(xmax)+' '+str(ymin)+' '+str(ymax)+'"')
#    os.system('xml_archangel -e '+sys.argv[ifile]+' mu_c '+str(central_mu))
    close('all')
    time.sleep(0.5)
    sys.exit()

  if event.key == '?': 
    print help()

  if event.key == 'c':
    rold=r1
    k=0.5+(event.xdata-i1)/(i2-i1)
    r1=r1*k
    if r1 < middle: r1=(rold-middle)/2.+middle
    r2=middle-0.05*(r1-middle)

  if event.key == 'i':
    rmin=1.e33
    if ifit == 2:
      xtest=(event.xdata)**4
    elif ifit == 0:
      xtest=10.**(event.xdata)
    elif ifit == 5:
      xtest=10.**(event.xdata)
    else:
      xtest=event.xdata
    for t in data:
      r=abs(t[0]-xtest)
      if r < rmin:
        rmin=r
        emin=t[0]

  if event.key in ['z','Z','r']:
    if event.key == 'z' and xxstep > 4.: xxstep=int(xxstep/2)+1
    if event.key == 'r': xxstep=int(2.*xxstep)-1
    if xxstep > nx/2:
      xxstep=nx/2
      i1=1
      i2=nx
      j1=1
      j2=ny
    else:
      i1=int(round((event.xdata)-xxstep)+1)
      i2=int(round((event.xdata)+xxstep)+1)
      if i1 < 1:
        i1=1
        i2=int(2*xxstep+i1)
      if i2 > nx:
        i1=int(nx-2*xxstep)
        i2=nx
      j1=int(round((event.ydata)-xxstep))
      j2=int(round((event.ydata)+xxstep))
      if j1 < 1:
        j1=1
        j2=int(2*xxstep+j1)
      if j2 > ny:
        j1=int(ny-2*xxstep)
        j2=ny

  if event.key == ',':
    inner_fit=event.xdata

  if event.key == '.':
    outer_fit=event.xdata

  if event.key == 'b':

    line='0 1\nparameters: values\n5 20\nxmin '+str(xmin)+'\nxmax '+str(xmax)+ \
         '\nymin '+str(ymin)+'\nymax '+str(ymax)+'\n'
    p = subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/widgets.py -entry_field -noadd', \
                         shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    tmp=p.communicate(line)[0]
    if '>>>aborting<<<' not in tmp:
      xmin=float(tmp.split('\n')[0])
      xmax=float(tmp.split('\n')[1])
      ymin=float(tmp.split('\n')[2])
      ymax=float(tmp.split('\n')[3])

  if event.key in ['shift']:
    pass
  else:
    clf()
    ax = fig.add_subplot(111)
    plot_bdd(False)

if __name__ == '__main__':

  if '-h' in sys.argv:
    print help()
    sys.exit()

  x1=x2=cstore=sstore=re_bulge=se_bulge=re_dev=se_dev=re_sersic=se_sersic=n_sersic='nan'

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

    try:
      sky=float(elements['sky'][0][1])
    except:
      sky=0.
    try:
      skysig=float(elements['skysig'][0][1])
    except:
      skysig=1.

    try:
      xscale=float(elements['scale'][0][1])
    except:
      xscale=1.
    try:
      cons=float(elements['zeropoint'][0][1])
    except:
      cons=25.

    try:
      k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05,'1563':0.10,'1564':0.10,'1565':0.10,'1566':0.10,'1391':0.10,'1494':0.10}
      exptime=float(elements['exptime'][0][1])
      if exptime != 0: # exptime = 0. signals all calibration in zeropoint, no airmass
        airmass=float(elements['airmass'][0][1])
        cons=2.5*log10(exptime)+cons
        cons=cons-k[elements['filter'][0][1]]*airmass
    except:
      pass

# ifit = 0, all fits
# ifit = 1, disk only fit
#      = 2, r^1/4 only fit
#      = 3, B+D fit, hold central disk sfb
#      = 4, B+D fit, all four parameters
#      = 5, Sersic fit

    try:
      re_sersic=float(elements['re_sersic'][0][1])
      se_sersic=float(elements['se_sersic'][0][1])
      n_sersic=float(elements['n_sersic'][0][1])
    except:
      pass

    if '-d' in sys.argv:
      x1=lower_fit_disk=float(elements['lower_fit_disk'][0][1])
      x2=upper_fit_disk=float(elements['upper_fit_disk'][0][1])
      chisq_disk=float(elements['chisq_disk'][0][1])
      cstore=float(elements['mu_o'][0][1])
      sstore=1.0857/float(elements['alpha'][0][1])
      ifit=1

    if '-c' in sys.argv:
      try:
        xc=float(elements['upper_fit_central'][0][1])
        cstore_c=float(elements['mu_c'][0][1])
        sstore_c=1.0857/float(elements['alpha_central'][0][1])
        ifit=6
      except:
        pass

    if '-b' in sys.argv:
      re_dev=float(elements['re_dev'][0][1])
      se_dev=float(elements['se_dev'][0][1])
      re_bulge=float(elements['re_bulge'][0][1])
      se_bulge=float(elements['se_bulge'][0][1])
      chisq_bulge=float(elements['chisq_bulge'][0][1])
      ifit=3

    if '-e' in sys.argv:
      lower_fit_dev=float(elements['lower_fit_dev'][0][1])
      upper_fit_dev=float(elements['upper_fit_dev'][0][1])
      x1=lower_fit_dev**0.25
      x2=upper_fit_dev**0.25
      re_dev=float(elements['re_dev'][0][1])
      se_dev=float(elements['se_dev'][0][1])
      chisq_dev=float(elements['chisq_dev'][0][1])
      ifit=2

    if '-s' in sys.argv or '-a' in sys.argv:
      lower_fit_sersic=float(elements['lower_fit_sersic'][0][1])
      upper_fit_sersic=float(elements['upper_fit_sersic'][0][1])
      chisq_sersic=float(elements['chisq_sersic'][0][1])
      x1=log10(lower_fit_sersic)
      x2=log10(upper_fit_sersic)
      if '-a' in sys.argv:
        ifit=0
      else:
        ifit=5

    try:
      origin=elements['origin'][0][1]
    except:
      origin=None

    isfb=0
    for t in elements['array']:
      if t[0]['name'] == 'prf':
        prf=[]
        data=[]
        head=[]
        for z in t[2]['axis']:
          prf.append(map(float,z[1].split('\n')))
          head.append(z[0]['name'])
        for z in range(len(prf[0])):
          err1=prf[head.index('RMSRES')][z]/(prf[head.index('NUM')][z])**0.5
          err2=skysig/(2.)**0.5 # note sqrt(2) kluge
          data.append([prf[head.index('RAD')][z],prf[head.index('INTENS')][z],1,(err1**2+err2**2)**0.5])
        tmp=array(prf)
        prf=swapaxes(tmp,1,0)
        if sys.argv[1] == '-p': break
      if t[0]['name'] == 'sfb' and sys.argv[1] != '-p':
        isfb=1
        data=[]
        tmp=[]
        head=[]
        for z in t[2]['axis']:
          head.append(z[0]['name'])
          tmp.append(map(float,z[1].split('\n')))
        for z in range(len(tmp[0])):
          if origin == '2MASS' and tmp[head.index('radius')][z] < 2.:
            kill=0
          else:
            kill=int(tmp[head.index('kill')][z])
          try: # if errorbars in sfb area
            data.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                         kill,tmp[head.index('error')][z]])
          except:
            data.append([tmp[head.index('radius')][z],tmp[head.index('mu')][z], \
                         kill,0.])
        break

    if x1 != x1: x1=data[0][0]
    if x2 != x2: x2=data[-1][0]

  except:
    raise
    print sys.argv[-1],'XML error'
    sys.exit()

  if 'prometheus' in os.uname()[1]:
    fig = figure(figsize=(12, 12), dpi=80)  # initialize plot parameters
    ax = fig.add_subplot(111)  # assign ax for text and axes
    manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager.window.title('')
    manager.window.geometry('+1200+300') # move the window for deepcore big screen
  else:
    fig = figure(figsize=(9, 9), dpi=80)  # initialize plot parameters
    ax = fig.add_subplot(111)  # assign ax for text and axes
    manager = get_current_fig_manager() # next 3 lines removes window title and sets geometry of Tk
    manager.window.title('')
    manager.window.geometry('+400+50')

  grey=0 ; nx=100. ; ny=100. ; outer_fit=5. ; inner_fit=0.

  if '-r' in sys.argv:
    files=['.fits']
  else:
    files=['.sub','.fake','.fits','.fit']

  for prefix in files:
    if os.path.exists(sys.argv[-1].split('.')[0]+prefix):
      fitsobj=pyfits.open(sys.argv[-1].split('.')[0]+prefix,"readonly")
      nx=fitsobj[0].header['NAXIS1']
      ny=fitsobj[0].header['NAXIS2']
      pix=fitsobj[0].data
      fitsobj.close()
      try:
        r1=float(elements['sfb_plot_contrast'][0][1].split()[0])
        middle=float(elements['sfb_plot_contrast'][0][1].split()[1])
        r2=float(elements['sfb_plot_contrast'][0][1].split()[2])
      except:
        r1=sky+50.*skysig
        r2=sky-0.05*(r1-sky)
        middle=sky
      try:
        i1=int(elements['sfb_plot_zoom'][0][1].split()[0])
        i2=int(elements['sfb_plot_zoom'][0][1].split()[1])
        j1=int(elements['sfb_plot_zoom'][0][1].split()[2])
        j2=int(elements['sfb_plot_zoom'][0][1].split()[3])
        xxstep=float(elements['sfb_plot_zoom'][0][1].split()[4])
      except:
        xxstep=nx/2
        i1=1
        i2=nx
        j1=1
        j2=ny
      grey=1
      break

  try:
    xmin=float(elements['sfb_plot_borders'][0][1].split()[0])
    xmax=float(elements['sfb_plot_borders'][0][1].split()[1])
    ymin=float(elements['sfb_plot_borders'][0][1].split()[2])
    ymax=float(elements['sfb_plot_borders'][0][1].split()[3])
  except:
    r=[] ; s=[] ; v=[] ; w=[] ; e=[]
    for t in data:
      for y in prf:
        if y[3]*xscale >= t[0]:
          tmp=(t[0]*t[0]*(1.-y[12]))**0.5
          break
      if t[2]:
        if ifit == 2:
          r.append(tmp**0.25)
        elif ifit == 0:
          r.append(log10(tmp))
        elif ifit == 5:
          r.append(log10(tmp))
        else:
          r.append(t[0])
        s.append(t[1])
        e.append(t[3])
      else:
        if ifit == 2:
          v.append(tmp**0.25)
        elif ifit == 0:
          v.append(log10(tmp))
        elif ifit == 5:
          v.append(log10(tmp))
        else:
          v.append(t[0])
        w.append(t[1])

#    xmin=min(r+v)-0.10*(max(r+v)-min(r+v))
    xmin=-5.
#    xmax=max(r+v)+0.10*(max(r+v)-min(r+v))
    xmax=max(r)+0.10*(max(r)-min(r))
    t=int(xmax) % 5
    xmax=int(xmax)+(5-t)
#    ymin=min(s+w)-0.10*(max(s+w)-min(s+w))
    ymin=18.
#    ymax=max(s+w)+0.10*(max(s+w)-min(s+w))
    ymax=27.
#    isw=1
#    while (isw):
#      isw=0
#      for t in data:
#        if ifit == 2:
#          t1=t[0]**0.25
#        elif ifit == 0:
#          t1=log10(t[0])
#        elif ifit == 5:
#          t1=log10(t[0])
#        else:
#          t1=t[0]
#        if t1 > xmin+(xmax-xmin)/2.2 and t[1] < ymax-(ymax-ymin)/2.2:
#          xmax=xmax+0.01*(xmax-xmin)
#          ymin=ymin-0.01*(ymax-ymin)
#          isw=1

  plot_bdd(False)
  cid=connect('key_press_event',clicker)
  show()
