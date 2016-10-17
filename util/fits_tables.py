#!/usr/bin/env python

import pyfits,sys,os

tab=pyfits.open(sys.argv[-1])
tabhdu=tab[1]
tabdat=tabhdu.data

for n in range(len(tabdat)):
  print str(tabdat[n]).replace('(','').replace(')','').replace(',','')
