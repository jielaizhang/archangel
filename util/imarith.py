#!/usr/bin/env python

import optparse, pyfits, os, os.path, sys

#p=optparse.OptionParser(description='Image arithmetic routine, copied from IRAF, operators = +,-,/,x,*',
#                        prog='imarith',
#                        usage='%prog input_image operator value/image output_image')
#options,arguments=p.parse_args()

#op=arguments[1]
op=sys.argv[-1].split()[1]
if op not in ['*','x','/','+','-']:
  print op,'is an illegal operation'
  sys.exit()
if op == 'x': op='*'

try:
  value=float(sys.argv[-1].split()[2])
except:
  value='data2'
  try:
    file=pyfits.open(sys.argv[-1].split()[2])
  except:
    print sys.argv[-1].split()[2],'not found'
    sys.exit()
  data2=file[0].data

try:
  file=pyfits.open(sys.argv[-1].split()[0].split('[')[0])
except:
  print sys.argv[-1].split()[0].split('[')[0],'not found'
  sys.exit()
nx=file[0].header['NAXIS1']
ny=file[0].header['NAXIS2']
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
data=file[0].data[y1:y2,x1:x2]

data=eval('data'+op+str(value))

if len(sys.argv[-1].split()) < 4:
  outfile=sys.argv[-1].split()[0].split('[')[0]
else:
  outfile=sys.argv[-1].split()[-1]

if os.path.exists(outfile):
  os.remove(outfile)

fitsobj=pyfits.HDUList()
hdu=pyfits.PrimaryHDU()
hdu.header=file[0].header
hdu.data=data
fitsobj.append(hdu)
fitsobj.writeto(outfile)
