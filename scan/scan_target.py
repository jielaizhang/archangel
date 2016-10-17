#!/usr//bin/env python

import sys,math,os

if sys.argv[1] == '-h':
  print 'Usage: find_target file xc yc'
  print ' '
  print '       options: -h = this message'
  print '                -s = dump mark file'
  print '                -v = verbose'
  sys.exit()

if sys.argv[-1].isdigit():
  filename=sys.argv[-3]
  xm=float(sys.argv[-2])
  ym=float(sys.argv[-1])
else:
  filename=sys.argv[-1]
  xm=0
  ym=0

if '-v' in sys.argv: print 'sky_box -f '+filename
sky=os.popen('sky_box -f '+filename).read()
if '-v' in sys.argv: print sky
if '-v' in sys.argv: print 'gasp_images -f '+filename+' '+sky.split()[2]+' '+str(10.*float(sky.split()[3]))+' 30 1'
images=os.popen('gasp_images -f '+filename+' '+sky.split()[2]+' '+str(10.*float(sky.split()[3]))+' 30 1').read()

if '-s' in sys.argv:
  for line in images.split('\n')[:-1]: print line
  sys.exit()

test=0.
for line in images.split('\n')[:-1]:
  area=float(line.split()[2])
  dr=((float(line.split()[0])-xm)**2+(float(line.split()[1])-ym)**2)**0.5
  if area/(dr+0.0001) > test:
#  if area > test:
    test=area/(dr+0.0001)
#    test=area
    xc=float(line.split()[0])
    yc=float(line.split()[1])
    rstop=(float(line.split()[2])/(math.pi*(1.-float(line.split()[3]))))**0.5
    eps=1.-float(line.split()[3])
    theta=float(line.split()[4])
    out=line[:-1]

if test == 0:
  print 'no target found'
  sys.exit()

print '%8.1f' % xc,
print '%8.1f' % yc,
print '%8.1f' % rstop,
print '%8.3f' % eps,
print '%8.1f' % theta
