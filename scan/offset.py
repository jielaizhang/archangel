#!/usr/bin/env python

import os,sys,pyfits

def do_master(i1,i2):
  tmp=[]
  for t in q1.split('\n')[:-1]:
    z=map(float,t.split())
    if z[3] < .15 and z[1] > 10 and z[1] < nx-10 and z[2] > 10 and z[2] < ny-10:
      rmin=1.e33
      for s in q1.split('\n')[:-1]:
        r=map(float,s.split())
        if ((r[0]-z[0])**2+(r[1]-z[1])**2)**0.5 > 0 and ((r[0]-z[0])**2+(r[1]-z[1])**2)**0.5 < rmin:
          rmin=((r[0]-z[0])**2+(r[1]-z[1])**2)**0.5
      if rmin > 20.:
        tmp.append(float(t.split()[-1]))
  tmp.sort()
  if len(tmp) <= 13:
    i1=-4 ; i2=-1
  master=[]
  if '-q' not in sys.argv: print '\nmaster:'
  for t in q1.split('\n')[:-1]:
    if float(t.split()[-1]) in tmp[i1:i2]:
      if '-q' not in sys.argv: print t
      master.append(map(float,t.split()))
  return master

def do_slave():
  if '-q' not in sys.argv: print '\nslave:'
  try:
    rmin=1.e33
    for first_line in q2.split('\n')[:-1]:
      w1=float(first_line.split()[0])
      z1=float(first_line.split()[1])
      for line in q2.split('\n')[:-1]:
        w2=float(line.split()[0])
        z2=float(line.split()[1])
        if abs(abs(w1-w2) - abs(master[0][0]-master[1][0])) < 1. and \
           abs(abs(z1-z2) - abs(master[0][1]-master[1][1])) < 1.:
          rr=((w1-master[0][0])**2+(z1-master[0][1])**2)**0.5
          if rr < rmin:
            rmin=rr
            hold=[first_line,w1-master[0][0],z1-master[0][1]]

    dx=[hold[1]]
    dy=[hold[2]]
    slave=[map(float,hold[0].split())]
    if '-q' not in sys.argv: print hold[0]

    rmin=1.e33
    for first_line in q2.split('\n')[:-1]:
      w1=float(first_line.split()[0])
      z1=float(first_line.split()[1])
      for line in q2.split('\n')[:-1]:
        w2=float(line.split()[0])
        z2=float(line.split()[1])
        if abs(abs(w1-w2) - abs(master[2][0]-master[1][0])) < 1. and \
           abs(abs(z1-z2) - abs(master[2][1]-master[1][1])) < 1.:
          rr=((w1-master[1][0])**2+(z1-master[1][1])**2)**0.5
          if rr < rmin:
            rmin=rr
            hold=[first_line,w1-master[1][0],z1-master[1][1]]

    dx.append(hold[1])
    dy.append(hold[2])
    slave.append(map(float,hold[0].split()))
    if '-q' not in sys.argv: print hold[0]

    rmin=1.e33
    for first_line in q2.split('\n')[:-1]:
      w1=float(first_line.split()[0])
      z1=float(first_line.split()[1])
      for line in q2.split('\n')[:-1]:
        w2=float(line.split()[0])
        z2=float(line.split()[1])
        if abs(abs(w1-w2) - abs(master[2][0]-master[0][0])) < 1. and \
           abs(abs(z1-z2) - abs(master[2][1]-master[0][1])) < 1.:
          rr=((w1-master[2][0])**2+(z1-master[2][1])**2)**0.5
          if rr < rmin:
            rmin=rr
            hold=[first_line,w1-master[2][0],z1-master[2][1]]

    dx.append(hold[1])
    dy.append(hold[2])
    slave.append(map(float,hold[0].split()))
    if '-q' not in sys.argv: print hold[0]

  except:
    pass
  try:
    return dx,dy
  except:
    return [],[]

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
#  return xmean2

if __name__ == "__main__":

  if '-h' in sys.argv:
    print './offset option master_file slave_file'
    print
    print 'option: -h = this message'
    print '        -q = quiet mode'
    print
    print 'offsets are such at master_coord = slave_coord - offset'
    sys.exit()

  fitsobj=pyfits.open(sys.argv[-2],"readonly")
  nx=fitsobj[0].header['NAXIS1']
  ny=fitsobj[0].header['NAXIS2']

  if '-q' not in sys.argv: print 'sky_box -f '+sys.argv[-2]
  sky=os.popen('sky_box -f '+sys.argv[-2]).read().split()
  if '-q' not in sys.argv: print 'sky = %5.1f' % float(sky[2]),
  if '-q' not in sys.argv: print 'sigma = %5.1f' % float(sky[3])
  if '-q' not in sys.argv: print 'gasp_images -f '+sys.argv[-2]+' '+sky[2]+' '+str(5*float(sky[3]))+' 10'
  q1=os.popen('gasp_images -f '+sys.argv[-2]+' '+sky[2]+' '+str(5*float(sky[3]))+' 10').read()
  if '-q' not in sys.argv: print len(q1.split('\n')),'targets found'

  if '-q' not in sys.argv: print ' '
  if '-q' not in sys.argv: print 'sky_box -f '+sys.argv[-1]
  sky=os.popen('sky_box -f '+sys.argv[-1]).read().split()
  if '-q' not in sys.argv: print 'sky = %5.1f' % float(sky[2]),
  if '-q' not in sys.argv: print 'sigma = %5.1f' % float(sky[3])
  if '-q' not in sys.argv: print 'gasp_images -f '+sys.argv[-1]+' '+sky[2]+' '+str(5*float(sky[3]))+' 10'
  q2=os.popen('gasp_images -f '+sys.argv[-1]+' '+sky[2]+' '+str(5*float(sky[3]))+' 10').read()
  if '-q' not in sys.argv: print len(q2.split('\n')),'targets found'

#  if len(tmp) < 10:
#    i1=-4 ; i2=-1
#  else:
#    i1=10 ; i2=13

  i1=10 ; i2=13
  master=do_master(i1,i2)
  ddx,ddy=do_slave()
  if ddx == []:
    if '-q' not in sys.argv: print '\n slaves not found, doing new master'
    i1=11 ; i2=14
    master=do_master(i1,i2)
    ddx,ddy=do_slave()

  dx=sum(ddx)/len(ddx)
  dy=sum(ddy)/len(ddy)

  if '-q' not in sys.argv:
    print
    print 'dx =','%.2f' % dx,'dy =','%.2f' % dy
    print

  x=[]
  y=[]
  for line in q1.split('\n')[:-1]:
    w=float(line.split()[0])
    z=float(line.split()[1])
#      mag=10.**(float(line.split()[5])/-2.5)
    rmin=+1.e33
    for i,line in enumerate(q2.split('\n')[:-1]):
#      print mag,mag-0.1*mag,line.split()[5],mag+0.1*mag
#      if float(line.split()[5]) < mag-0.1*mag and float(line.split()[5]) > mag+0.1*mag:
      r=((w+dx-float(line.split()[0]))**2+(z+dy-float(line.split()[1]))**2)**0.5
#      r=r*abs(mag-10.**(float(line.split()[5])/-2.5))/mag
      if r < rmin:
        imin=i
        rmin=r

#    print rmin,w+dx-float(q2.split('\n')[imin].split()[0]),z+dy-float(q2.split('\n')[imin].split()[1])
    x.append(w+dx-float(q2.split('\n')[imin].split()[0]))
    y.append(z+dy-float(q2.split('\n')[imin].split()[1]))
#  print itmean(x,3), itmean(y,3)
  xsh=float(itmean(x,3))+dx
  ysh=float(itmean(y,3))+dy
  if '-q' not in sys.argv:
    print 'Offset is x =','%.2f' % xsh,'y =','%.2f' % ysh
  else:
    print '%.2f' % xsh,'%.2f' % ysh
