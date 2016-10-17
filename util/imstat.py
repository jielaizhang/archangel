#!/usr/bin/env python

import sys, pyfits, os, os.path, math, numpy

# special unix alias "\*!" to capture []'s, but all sys.argv[-1] one line

# note: pull back by 1 for lower x,y, ok on upper, to match
# iraf imstat which is not inclusive, so 100:200 is really 100 to 199
# note range does not do last value

if '-h' in sys.argv:
  print 'imstat - do images statistic (IRAF like)'
  print
  print 'give it file name and [] regions, not .cshrc fix'
  print 'takes wildcards'
  print '-q suppress header and writes to imstat.tmp'
  sys.exit()

if '*' in sys.argv[-1].replace('-q ',''):
  files=list(os.popen('ls '+sys.argv[-1].replace('-q ','').split('[')[0]).read().split('\n')[:-1])
else:
  files=[sys.argv[-1].replace('-q ','')]

if '-q' in sys.argv[-1]: fout=open('imstat.tmp','w')

file_length=max(list(len(filename.split('[')[0]) for filename in files))

for ifile,filename in enumerate(files):
  try:
    file=pyfits.open(filename.split('[')[0])
    data=file[0].data
    nx=file[0].header['NAXIS1']
    ny=file[0].header['NAXIS2']
  except:
    print 'file error for',filename
  width=int(math.log10(nx))+int(math.log10(ny))+5
  if '[' in sys.argv[-1]:
    try:
      x1=int(sys.argv[-1].split('[')[1].split(':')[0])-1
      x2=int(sys.argv[-1].split('[')[1].split(':')[1].split(',')[0])
    except:
      x1=0 ; x2=nx
    try:
      y1=int(sys.argv[-1].split(',')[1].split(':')[0])-1
      y2=int(sys.argv[-1].split(',')[1].split(':')[1].split(']')[0])
    except:
      y1=0 ; y2=ny
  else:
    x1=0 ; x2=nx ; y1=0 ; y2=ny
  if x2 > nx: x2=nx
  if y2 > ny: y2=ny
  if x1+1 >= x2: x1=0
  if y1+1 >= y2: y1=0
  width=len('['+str(x1+1)+':'+str(x2)+','+str(y1+1)+':'+str(y2)+']')

#  sum=0. ; n=0 ; imax=-1.e33 ; imin=+1.e33 ; num_nan=0
#  for j in range(y1,y2):
#    for i in range(x1,x2):
#      if data[j][i] == data[j][i]:
#        sum=sum+data[j][i]
#        n+=1
#        if data[j][i] < imin:
#          imin=data[j][i]
#          xmin=i+1
#          ymin=j+1
#        if data[j][i] > imax:
#          imax=data[j][i]
#          xmax=i+1
#          ymax=j+1
#      else:
#        num_nan=num_nan+1

  imin=numpy.min(data[y1:y2,x1:x2])
  ymin=int(numpy.argmin(data[y1:y2,x1:x2])/nx)+1
  xmin=int(numpy.argmin(data[y1:y2,x1:x2])-nx*int(numpy.argmin(data[y1:y2,x1:x2])/nx))+1
  imax=numpy.max(data[y1:y2,x1:x2])
  ymax=int(numpy.argmax(data[y1:y2,x1:x2])/nx)+1
  xmax=int(numpy.argmax(data[y1:y2,x1:x2])-nx*int(numpy.argmax(data[y1:y2,x1:x2])/nx))+1
  zm=numpy.ma.masked_where(numpy.isnan(data[y1:y2,x1:x2]), data[y1:y2,x1:x2])
  zm.mean()
  zm.std()
  sum=zm.sum()
  num_nan=numpy.isnan(data[y1:y2,x1:x2]).sum()
  n=(y2-y1)*(x2-x1)-num_nan

  if '-q' not in sys.argv[-1] and not ifile:
    print 'file'.ljust(file_length),
    print '    array'.ljust(width),
    print '    sum    ',
    print '  npix   ',
    print '  mean   ',
    tmp='('+str(xmin)+','+str(ymin)+')'
    print '    min'.ljust(len(tmp)+2),
    tmp='('+str(xmax)+','+str(ymax)+')'
    print '               max'.ljust(len(tmp)+2),
    print '                 nan'

  print filename.split('[')[0].ljust(file_length),
  if '-q' in sys.argv[-1]: print >> fout,filename.split('[')[0].ljust(file_length),
  tmp='['+str(x1+1)+':'+str(x2)+','+str(y1+1)+':'+str(y2)+']'
  print tmp.ljust(width),
  if '-q' in sys.argv[-1]: print >> fout,tmp.ljust(width),
  if sum > 99999.:
    print '%10.2e' % sum,
    if '-q' in sys.argv[-1]: print >> fout,'%10.2e' % sum,
  else:
    print '%10.2f' % sum,
    if '-q' in sys.argv[-1]: print >> fout,'%10.2f' % sum,
  if n > 99999:
    print '%7.2e' % n,
    if '-q' in sys.argv[-1]: print >> fout,'%7.2e' % n,
  else:
    print '%7.0i' % n,
    if '-q' in sys.argv[-1]: print >> fout,'%7.0i' % n,
  if sum/n > 99999.:
    print '%10.3e' % (sum/n),
    if '-q' in sys.argv[-1]: print >> fout,'%10.3e' % (sum/n),
  else:
    print '%10.3f' % (sum/n),
    if '-q' in sys.argv[-1]: print >> fout,'%10.3f' % (sum/n),
  if abs(imin) > 99999:
    print '%10.2e' % imin,
    if '-q' in sys.argv[-1]: print >> fout,'%10.2e' % imin,
  else:
    print '%10.2f' % imin,
    if '-q' in sys.argv[-1]: print >> fout,'%10.2f' % imin,
  tmp='('+str(xmin)+','+str(ymin)+')'
  print tmp.ljust(len(tmp)+2),
  if '-q' in sys.argv[-1]: print >> fout,tmp.ljust(len(tmp)+2),
  if abs(imax) > 99999:
    print '%10.2e' % imax,
    if '-q' in sys.argv[-1]: print >> fout,'%10.2e' % imax,
  else:
    print '%10.2f' % imax,
    if '-q' in sys.argv[-1]: print >> fout,'%10.2f' % imax,
  tmp='('+str(xmax)+','+str(ymax)+')'
  print tmp.ljust(len(tmp)+2),
  if '-q' in sys.argv[-1]: print >> fout,tmp.ljust(len(tmp)+2),
  if abs(num_nan) > 99999:
    print '%10.2e' % num_nan
    if '-q' in sys.argv[-1]: print >> fout,'%10.2e' % num_nan
  else:
    print '%10.1i' % num_nan
    if '-q' in sys.argv[-1]: print >> fout,'%10.1i' % num_nan
if '-q' in sys.argv[-1]: fout.close()
