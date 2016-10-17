#!/usr/bin/env python

import os,sys,math

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print ' '
  print 'Usage: extreme_lsb op file_name xc yc max_rad no_clean_radius'
  print ' '
  print 'finds ellipses for extreme LSB objects'
  print
  print 'Options: -c = no clean'
  print '         -i = do inner 4 pixels'
  sys.exit()

if '-c' in sys.argv:
  ii=1
else:
  ii=0
  no_clean_rad=float(sys.argv[-1])

if sys.argv[-5+ii].find('.') == -1:
  prefix=sys.argv[-5+ii]
  endfix='fits'
else:
  prefix=sys.argv[-5+ii].split('.')[0]
  endfix=sys.argv[-5+ii].split('.')[1]

xc=float(sys.argv[-4+ii])
yc=float(sys.argv[-3+ii])
lx=int(sys.argv[-2+ii])

# get sky

try:
  xsky=float(os.popen('xml_archangel -o '+prefix+' sky').read())
  skysig=float(os.popen('xml_archangel -o '+prefix+' skysig').read())
except:
  print 'no sky found, please determine sky'
  cmd='probe '+prefix+'.fits'
  tmp=os.popen(cmd).read()
  xsky=float(os.popen('xml_archangel -o '+prefix+' sky').read())
  skysig=float(os.popen('xml_archangel -o '+prefix+' skysig').read())

# first isophotes

cmd='thres_prf '+prefix+'.'+endfix+' '+str(xc)+' '+str(yc)+' > tmp.prf'
print '\n'+cmd
os.system(cmd)

# correct angles

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

# set up the radii for ellipses (note starts at 4 pixels)

if '-i' in sys.argv:
  x=5.
  rad=[x]
  while 1:
    x=x/1.2
    if x < 1: break
    rad.append(x)
  x=5.
else:
  rad=[4.] ; x=4.

while 1:
  x=x*1.2
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

open('tmp.tmp','w').write('INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 '+ \
                          'RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n')
cmd='cat tmp.tmp tmp.prf | xml_archangel -a '+prefix+' prf'
print '\n'+cmd
os.system(cmd)

cmd='probe -t '+prefix+'.fits'
print '\n'+cmd
tmp=os.popen(cmd).read()
if 'abort' in tmp: sys.exit()

cmd='xml_archangel -o '+prefix+' prf | lines 2- > tmp.prf'
print '\n'+cmd
os.system(cmd)

cmd='prf_smooth -q tmp.prf | grep -v "nan" > tmp.tmp'
print '\n'+cmd
tmp=os.popen(cmd).read()
if len(tmp) > 0: print tmp

if sys.argv[1] != '-c':
  cmd='prf_clean -s '+prefix+'.'+endfix+' tmp.tmp 5 '+str(no_clean_rad)
  print '\n'+cmd
  os.system(cmd)
  if os.path.isfile(prefix+'.prf_clean'):
    cmd='mv -f '+prefix+'.prf_clean '+prefix+'.clean'
    os.system(cmd)

  cmd='thres_prf '+prefix+'.clean '+str(xc)+' '+str(yc)+' > tmp.prf'
  print '\n'+cmd
  os.system(cmd)

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

  if '-i' in sys.argv:
    x=5.
    rad=[x]
    while 1:
      x=x/1.2
      if x < 1: break
      rad.append(x)
    x=5.
  else:
    rad=[4.] ; x=4.

  while 1:
    x=x*1.2
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

  cmd='prf_smooth -q tmp.prf > tmp.tmp'
  print '\n'+cmd
  os.system(cmd)

cmd='iso_prf -q '+prefix+'.clean tmp.tmp -sg 0 | grep -v NAN > tmp.prf'
print '\n'+cmd
os.system(cmd)

open('tmp.tmp','w').write('INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 '+ \
                          'RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n')
cmd='cat tmp.tmp tmp.prf | xml_archangel -a '+prefix+' prf'
print '\n'+cmd
os.system(cmd)
os.remove('tmp.tmp')
os.remove('tmp.prf')

if '-c' not in sys.argv:
  cmd='probe -t '+prefix+'.fits'
  print '\n'+cmd
  tmp=os.popen(cmd).read()

#if tmp.find('tmp.prf') > 0:
#  cmd='iso_prf -q '+prefix+'.'+endfix+' tmp.prf -sg 0 | grep -v NAN > '+prefix+'.prf'
#  print '\n'+cmd
#  os.system(cmd)
#
#open('tmp.tmp','w').write('INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 '+ \
#                          'RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n')
#cmd='cat tmp.tmp '+prefix+'.prf | xml_archangel -a '+prefix+' prf'
#print cmd
#os.system(cmd)
