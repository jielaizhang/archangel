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
  return '%7.1f' % xmean2

if __name__ == "__main__":
  if sys.argv[1] == '-v':
    idx=2
  else:
    idx=1
  if idx == 2: print 'sky_box -f '+sys.argv[idx]
  sky=string.split(os.popen('~/archangel/bin/sky_box -f '+sys.argv[idx]).read())
  if idx == 2: print 'sky = %5.1f' % float(sky[2]),
  if idx == 2: print 'sigma = %5.1f' % float(sky[3])
  if idx == 2: print 'gasp_images -f '+sys.argv[idx]+' '+sky[2]+' '+str(5*float(sky[3]))+' 10 > quick1.tmp'
  os.system('~/archangel/bin/gasp_images -f '+sys.argv[idx]+' '+sky[2]+' '+str(5*float(sky[3]))+' 10 > quick1.tmp')
  out=os.popen('wc quick1.tmp').read()
  if idx == 2: print string.split(out)[0]+' targets found'

  for name in sys.argv[idx+1:]:
    if idx == 2: print ' '
    if idx == 2: print 'sky_box -f '+name
    sky=string.split(os.popen('~/archangel/bin/sky_box -f '+name).read())
    if idx == 2: print 'sky = %5.1f' % float(sky[2]),
    if idx == 2: print 'sigma = %5.1f' % float(sky[3])
    if idx == 2: print 'gasp_images -f '+name+' '+sky[2]+' '+str(5*float(sky[3]))+' 10 > quick2.tmp'
    os.system('~/archangel/bin/gasp_images -f '+name+' '+sky[2]+' '+str(5*float(sky[3]))+' 10 > quick2.tmp')
    out=os.popen('wc quick2.tmp').read()
    if idx == 2: print string.split(out)[0]+' targets found'

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
      if float(line.split()[3]) < 0.2:
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

    if idx == 2: print len(x),'matches in x'
    xsh=itmean(x,3)
    if idx == 2: print len(y),'matches in y'
    ysh=itmean(y,3)
    if idx == 2: print xsh,ysh

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
      if float(line.split()[3]) < 0.2:
        while 1:
          line=file2.readline()
          if not line: break
          if (w-float(line.split()[0]) > float(xsh)-5) and (w-float(line.split()[0]) < float(xsh)+5) and \
             (z-float(line.split()[1]) > float(ysh)-5) and (z-float(line.split()[1]) < float(ysh)+5): 
            x.append(w-float(line.split()[0]))
            y.append(z-float(line.split()[1]))
        file2.close()
    file1.close()

    if idx == 2: print len(x),'matches in x'
    xsh=itmean(x,3)
    if idx == 2: print len(y),'matches in y'
    ysh=itmean(y,3)
    if idx == 2: print xsh,ysh

    print 'imshift',name,name.replace('f.','a.'),xsh,ysh
