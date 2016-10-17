#!/usr/bin/env python

import sys, os, math

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
      if sig2 == 0.: return xmean1,sig1,xmean2,sig2,len(x),npts,its
    except:
      return xmean1,sig1,'NaN','NaN',len(x),'NaN','NaN'
  return xmean1,sig1,xmean2,sig2,len(x),npts,its

if '-h' in sys.argv:
  print './short_calib.py short.fits long.fits'
  sys.exit()

exp1=float(os.popen('keys -p '+sys.argv[-2]+' | grep EXPTIME').read().split()[2])
nx=int(os.popen('keys -p '+sys.argv[-2]+' | grep NAXIS1').read().split()[2])
ny=int(os.popen('keys -p '+sys.argv[-2]+' | grep NAXIS2').read().split()[2])
exp2=float(os.popen('keys -p '+sys.argv[-1]+' | grep EXPTIME').read().split()[2])
if '-q' not in sys.argv:
  print 'Exp Times:',exp1,exp2
  print 'offset -q '+sys.argv[-2]+' '+sys.argv[-1]
off=os.popen('offset -q '+sys.argv[-2]+' '+sys.argv[-1]).read()
sky=os.popen('sky_box -f '+sys.argv[-2]).read().split()
q1=os.popen('gasp_images -f '+sys.argv[-2]+' '+sky[2]+' '+str(5*float(sky[3]))+' 10').read()
if '-q' not in sys.argv:
  print 'Offsets:',off
  print 'gasp_images -f '+sys.argv[-2]+' '+sky[2]+' '+str(5*float(sky[3]))+' 10'
  print len(q1.split('\n')[:-1]),'targets'
file=open('in1.tmp','w')
for t in q1.split('\n')[:-1]:
  if float(t.split()[3]) < 0.2 and float(t.split()[0]) > 50 and float(t.split()[0]) < nx-50 and \
     float(t.split()[1]) > 50 and float(t.split()[1]) < ny-50:
    print >> file,t.split()[0]+' '+t.split()[1]+' '+str(2.*(float(t.split()[2])/math.pi)**0.5)
file.close()
if '-q' not in sys.argv:
  print '~/archangel/phot/spot_apert.py '+sys.argv[-2]+' < in1.tmp'
mag1=os.popen('~/archangel/phot/spot_apert.py '+sys.argv[-2]+' < in1.tmp').read()

file=open('in2.tmp','w')
for t in q1.split('\n')[:-1]:
  if float(t.split()[3]) < 0.2 and float(t.split()[0]) > 50 and float(t.split()[0]) < nx-50 and \
     float(t.split()[1]) > 50 and float(t.split()[1]) < ny-50:
    print >> file,str(float(t.split()[0])+float(off.split()[0]))+' '+ \
                  str(float(t.split()[1])+float(off.split()[1]))+' '+ \
                  str(2.*(float(t.split()[2])/math.pi)**0.5)
file.close()
if '-q' not in sys.argv:
  print '~/archangel/phot/spot_apert.py '+sys.argv[-1]+' < in2.tmp'
mag2=os.popen('~/archangel/phot/spot_apert.py '+sys.argv[-1]+' < in2.tmp').read()

test=[]
file=open('out.tmp','w')
if '-q' not in sys.argv:
  print len(mag1.split('\n')[:-1]),len(mag2.split('\n')[:-1])
for x,y in zip(mag1.split('\n')[:-1],mag2.split('\n')[:-1]):
  if 'nan' not in x and 'nan' not in y:
    test.append((10.**(float(x.split()[0])/-2.5)/exp1)/(10.**(float(y.split()[0])/-2.5)/exp2))
    print >> file,x.split()[0],y.split()[0],10.**(float(x.split()[0])/-2.5)/exp1,10.**(float(y.split()[0])/-2.5)/exp2
file.close()
print sys.argv[-2],xits(test,3.)
