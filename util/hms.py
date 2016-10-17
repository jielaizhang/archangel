#!/usr/bin/env python

import sys

if sys.argv[1] == '-h':
  print 'hms = convert from decimal to HMS (-d) or HMS to decimal (default)'
  sys.exit()

if sys.argv[1] == '-d':
  ra=float(sys.argv[-2])
  dec=float(sys.argv[-1])
  ra=24.*ra/360.
  print '%2.2i' % int(round(ra,4))+'h',
  mn=60.*(ra-int(round(ra,4)))
  print '%2.2i' % int(round(mn,2))+'m',
  sec=60.*(mn-int(round(mn,2)))
  if sec < 10:
    print '0'+'%4.2f' % abs(sec)+'s',
  else:
    print '%5.2f' % abs(sec)+'s',

  if dec < 0:
    sign='-'
  else:
    sign='+'
  dec=abs(dec)
  print sign+'%2.2i' % int(round(dec,4))+'d',
  mn=60.*(dec-int(round(dec,4)))
  print '%2.2i' % int(round(mn,2))+'m',
  sec=60.*(mn-int(round(mn,2)))
  if sec < 10:
    print '0'+'%3.1f' % abs(sec)+'s',
  else:
    print '%4.1f' % abs(sec)+'s',

else:

  sign='+'
  if len(sys.argv) == 3 and ':' not in sys.argv[-1]:
    tmp=sys.argv[1]
    for t in ['h','m','s']:
      tmp=tmp.replace(t,' ')
    hr=mn=sec=0.
    try:
      hr=float(tmp.split()[0])
      mn=float(tmp.split()[1])
      sec=float(tmp.split()[2])
    except:
      pass
    ra=360.*(hr+mn/60.+sec/3600.)/24.
    tmp=sys.argv[2]
    if tmp[0] == '-': sign='-'
    for t in ['d','m','s']:
      tmp=tmp.replace(t,' ')
    hr=mn=sec=0.
    try:
      hr=float(tmp.split()[0])
      mn=float(tmp.split()[1])
      sec=float(tmp.split()[2])
    except:
      pass
  elif ':' in sys.argv[-1]:
    hr=float(sys.argv[1].split(':')[0])
    mn=float(sys.argv[1].split(':')[1])
    sec=float(sys.argv[1].split(':')[2])
    ra=360.*(hr+mn/60.+sec/3600.)/24.
    if sys.argv[-1][0] == '-': sign='-'
    hr=abs(float(sys.argv[-1].split(':')[0]))
    mn=float(sys.argv[-1].split(':')[1])
    sec=float(sys.argv[-1].split(':')[2])

  else:
    hr=float(sys.argv[1].replace('h',''))
    mn=float(sys.argv[2].replace('m',''))
    sec=float(sys.argv[3].replace('s',''))
    ra=360.*(hr+mn/60.+sec/3600.)/24.
    if sys.argv[4][0] == '-': sign='-'
    hr=abs(float(sys.argv[4].replace('d','')))
    mn=float(sys.argv[5].replace('m',''))
    sec=float(sys.argv[6].replace('s',''))

  print '%10.6f' % ra,
  if sign == '-':
    print '%11.6f' % (-1.*(hr+mn/60.+sec/3600.))
  else:
    print '%11.6f' % (hr+mn/60.+sec/3600.)
