#!/usr/bin/env python

import os,sys,math

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print ' '
  print 'Usage: brute_prf file_name xc yc area'
  print ' '
  print 'finds ellipses for extreme LSB objects'
  sys.exit()

if sys.argv[1].find('.') == -1:
  prefix=sys.argv[1]
  endfix='fits'
else:
  prefix=sys.argv[1].split('.')[0]
  endfix=sys.argv[1].split('.')[1]

if len(sys.argv) < 3:
  cmd='keys -p '+sys.argv[1]+' | grep NAXIS1'
  nx=int(os.popen(cmd).read().split()[2])
  cmd='keys -p '+sys.argv[1]+' | grep NAXIS2'
  ny=int(os.popen(cmd).read().split()[2])
else:
  nx=sys.argv[2]
  ny=sys.argv[3]

if len(sys.argv) <= 4:
  lara=100.
else:
  lara=float(sys.argv[4])

cmd='keys -p '+sys.argv[1]+' | grep NAXIS1'
lx=int(os.popen(cmd).read().split()[2])

file=open('tmp.prf','r')
e=[]
lastang=0.
while 1:
  line=file.readline()
  if not line: break
  array=line.split()
  ell=[float(array[3])]
  ell.append(float(array[12]))
  if abs(float(array[13])-lastang) > 90 and lastang != 0.:
    lastang=float(array[13])+180.
  else:
    lastang=float(array[13])
  ell.append(lastang)
  ell.append(float(array[14]))
  ell.append(float(array[15]))
  e.append(ell)
e.sort()

x=5.
rad=[x]
while 1:
  x=x/1.1
  if x < 1: break
  rad.append(x)
x=5.
while 1:
  x=x*1.1
  if x > lx/2: break
  rad.append(x)
rad.sort()

outfile=open('tmp.prf','w')
for n in rad:
  if n <= e[0][0]:
    print >> outfile,'0. 0. 0.',n,'0. 0. 1. 0. 0. 0. 0. 0.',e[0][1],e[0][2],e[0][3],e[0][4],'0. 0.'
  elif n >= e[-1][0]:
    print >> outfile,'0. 0. 0.',n,'0. 0. 1. 0. 0. 0. 0. 0.',e[-1][1],e[-1][2],e[-1][3],e[-1][4],'0. 0.'
  else:
    for x in e[1:]:
      i=e.index(x)
      if x[0] > n:
        print >> outfile,'0. 0. 0.',n,'0. 0. 1. 0. 0. 0. 0. 0.',
        for y in x[1:]:
          j=x.index(y)
          tmp=y+(e[i-1][j]-y)*(n-x[0])/(e[i-1][0]-x[0])
          print >> outfile,tmp,
        print >> outfile,'0. 0.'
        break
outfile.close()

cmd='iso_prf -q '+prefix+'.'+endfix+' tmp.prf -sg 0 | grep -v NAN > '+prefix+'.prf'
print '\n'+cmd
os.system(cmd)

cmd='prf_clean -s '+prefix+'.'+endfix+' '+prefix+'.prf 5'
print '\n'+cmd
os.system(cmd)
if os.path.isfile(prefix+'.prf_clean'):
  cmd='mv -f '+prefix+'.prf_clean '+prefix+'.clean'
  os.system(cmd)

cmd='iso_prf -q '+prefix+'.'+endfix+' tmp.prf -sg 0 | grep -v NAN > '+prefix+'.prf'
print '\n'+cmd
os.system(cmd)

cmd='prf_edit '+prefix+'.clean'
print '\n'+cmd
tmp=os.popen(cmd).read()
if tmp.find('tmp.prf') > 0:
  cmd='iso_prf -q '+prefix+'.'+endfix+' tmp.prf -sg 0 | grep -v NAN > '+prefix+'.prf'
  print '\n'+cmd
  os.system(cmd)

cmd='mark '+prefix+'.prf > s.tmp'
print '\n'+cmd
os.system(cmd)
