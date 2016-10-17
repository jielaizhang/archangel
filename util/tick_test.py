#!/usr/bin/env python

import sys
import math
import numarray

xmin=float(sys.argv[-2])
xmax=float(sys.argv[-1])

r=abs(xmax-xmin)
r=round(r/(10.**int(math.log10(r))),9)

i1=0
i2=-10
dd=-1
print 
for n in range(i1,i2,dd):
#  print '%3.1i' % n,
#  print '%6.1f' % (r/(10.**(n))),
#  print '%6.1i' % (int(round(r/(10.**(n)),1))),
#  print '%6.1i' % (int(round(r/(10.**(n)),1))//((r/(10.**(n)))))
  if int(round(r/(10.**(n)),1))//((r/(10.**(n)))) == 1: break

if   int(round(r/(10.**(n)),1)) == 1:
  print (r/4.)*(10.**int(math.log10(abs(xmax-xmin))))
elif int(round(r/(10.**(n)),1)) == 2:
  print (r/4.)*(10.**int(math.log10(abs(xmax-xmin))))
elif int(round(r/(10.**(n)),1)) == 3:
  print (r/3.)*(10.**int(math.log10(abs(xmax-xmin))))
elif int(round(r/(10.**(n)),1)) == 4:
  print (r/4.)*(10.**int(math.log10(abs(xmax-xmin))))
elif int(round(r/(10.**(n)),1)) == 5:
  print (r/5.)*(10.**int(math.log10(abs(xmax-xmin))))
elif int(round(r/(10.**(n)),1)) == 6:
  print (r/3.)*(10.**int(math.log10(abs(xmax-xmin))))
elif int(round(r/(10.**(n)),1)) == 7:
  print (r/7.)*(10.**int(math.log10(abs(xmax-xmin))))
elif int(round(r/(10.**(n)),1)) == 8:
  print (r/4.)*(10.**int(math.log10(abs(xmax-xmin))))
elif int(round(r/(10.**(n)),1)) == 9:
  print (r/3.)*(10.**int(math.log10(abs(xmax-xmin))))

sys.exit()

if r == 1:
  print 0.25*(10.**int(math.log10(abs(xmax-xmin))))
elif int(math.log10(r))//math.log10(r) == 1:
  print (r/4.)*(10.**int(math.log10(abs(xmax-xmin))))
else:
  i1=0
  i2=-10
  dd=-1
  print 
  for n in range(i1,i2,dd):
    print '%3.1i' % n,
    print '%6.1f' % (r/(10.**(n))),
    print '%6.1i' % (int(round(r/(10.**(n)),1))),
    print '%6.1i' % (int(round(r/(10.**(n)),1))//((r/(10.**(n)))))
    if int(round(r/(10.**(n)),1))//((r/(10.**(n)))) == 1: break
  print

  ntest=n
  print '          ntest'

  for x in numarray.arange(9.,0.,-1.):
    z=r/x
    for n in range(i1,i2,dd):
      if int(round(z/(10.**(n)),1))//((z/(10.**(n)))) == 1: break
    print '%3.1f' % x,'%4.1i' % n,'%4.1i' % ntest,
    print '%4.1i' % (int(round(z/(10.**(n)),1))//((z/(10.**(n))))),
    print '%.5f' % z,
    print '%.5f' % (z*(10.**int(math.log10(abs(xmax-xmin))))),
    print '%.5f' % (z/(10.**(int(math.log10(z))-1)))
  print

  for x in numarray.arange(9.,0.,-1.):
    z=r/x
    for n in range(i1,i2,dd):
      if int(round(z/(10.**(n)),1))//((z/(10.**(n)))) == 1: break
#    if abs(n) <= abs(ntest): break
#    print '%.5f' % (z/(10.**(int(math.log10(z))-1)))
    if round(z/(10.**(int(math.log10(z))-1)),4) == 5: break

  print z*(10.**int(math.log10(abs(xmax-xmin))))

