#!/usr/bin/env python

import os,sys,string

def itmean(x,xsig):
  xmean1=0.
  sig1=0.
  n=0
  for data in x:
    n=n+1
    xmean1=xmean1+data
  xmean1=xmean1/n
  for data in x:
    sig1=sig1+(data-xmean1)**2
  sig1=(sig1/(n-1))**.5
#  print '%7.1f' % xmean1,
#  print '%7.1f' % sig1,
#  print '%4.0i' % n
  sig2=sig1
  xmean2=xmean1
  xold=xmean2+1
  its=0
  while xold != xmean2:
    xold=xmean2
    its=its+1
    dum=0.
    npts2=0
    for data in x:
      if abs(data-xold) <= xsig*sig2:
        npts2=npts2+1
        dum=dum+data
    xmean2=dum/npts2
    dum=0.
    for data in x:
      if abs(data-xold) <= xsig*sig2:
        dum=dum+(data-xmean2)**2
    sig2=(dum/(npts2-1))**.5
#    print '%7.1f' % xmean2,
#    print '%7.1f' % sig2,
#    print '%4.0i' % npts2
#  return '%7.1f' % xmean2
  return xmean2

if __name__ == "__main__":
  print 'sky_box -f '+sys.argv[1]
  sky=string.split(os.popen('~/archangel/sky/sky_box -f '+sys.argv[1]).read())
  print 'sky = %5.1f' % float(sky[2]),
  print 'sigma = %5.1f' % float(sky[3])
  print 'gasp_images -f '+sys.argv[1]+' '+sky[2]+' '+str(5*float(sky[3]))+' 10 > quick1.tmp'
  os.system('~/archangel/bin/gasp_images -f '+sys.argv[1]+' '+sky[2]+' '+str(5*float(sky[3]))+' 10 > quick1.tmp')
  out=os.popen('wc quick1.tmp').read()
  print string.split(out)[0]+' targets found'

  for name in sys.argv[2:]:
    print ' '
    print 'sky_box -f '+name
    sky=string.split(os.popen('~/archangel/sky/sky_box -f '+name).read())
    print 'sky = %5.1f' % float(sky[2]),
    print 'sigma = %5.1f' % float(sky[3])
    print 'gasp_images -f '+name+' '+sky[2]+' '+str(5*float(sky[3]))+' 10 > quick2.tmp'
    os.system('~/archangel/bin/gasp_images -f '+name+' '+sky[2]+' '+str(5*float(sky[3]))+' 10 > quick2.tmp')
    out=os.popen('wc quick2.tmp').read()
    print string.split(out)[0]+' targets found'

    file1=open('quick1.tmp','r')

    x=[]
    y=[]
    while 1:
      line=file1.readline()
      if not line: break
      w=float(line.split()[0])
      z=float(line.split()[1])
      mag=float(line.split()[5])
      file2=open('quick2.tmp','r')
      while 1:
        line=file2.readline()
        if not line: break
        if float(line.split()[5]) > mag-0.1*mag and float(line.split()[5]) < mag+0.1*mag:
          r=((w-float(line.split()[0]))**2+(z-float(line.split()[1]))**2)**0.5
          if r < 50: 
            x.append(w-float(line.split()[0]))
            y.append(z-float(line.split()[1]))
      file2.close()
    file1.close()
    xsh=-int(itmean(x,3))
    ysh=-int(itmean(y,3))

    print     '~/archangel/util/mask '+name+' '+sys.argv[1].replace('c','e')+' '+name.replace('c','e')+\
              ' '+str(xsh).lstrip()+' '+str(ysh).lstrip()
    os.system('~/archangel/util/mask '+name+' '+sys.argv[1].replace('c','e')+' '+name.replace('c','e')+\
              ' '+str(xsh).lstrip()+' '+str(ysh).lstrip())
