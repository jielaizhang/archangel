#!/usr/bin/env python

import os, sys

prefix=sys.argv[-1].split('.')[0]
nx=int(os.popen('keys -p '+prefix+'.fits | grep NAXIS1').read().split('=')[1])
ny=int(os.popen('keys -p '+prefix+'.fits | grep NAXIS2').read().split('=')[1])

if nx > ny:
  stop=nx
else:
  stop=ny

data=os.popen('xml_archangel -o '+prefix+' prf | lines 2-').read().split('\n')
step=float(data[-2].split()[3])

out=open('tmp.prf','w')
for z in data[:-1]:
  out.write(z+'\n')

while (1):
  step=0.1*step+step
  if step > stop: break
  out.write(' '.join(z.split()[0:3])+' '+str(step)+' '+' '.join(z.split()[4:])+'\n')
out.close()

cmd='iso_prf -q '+prefix+'.clean tmp.prf -sg 0 > tmp2.prf'
print cmd
os.system(cmd)
out=os.popen('wc tmp2.prf').read()
print out.split()[0]+' ellipses found'

open('tmp.tmp','w').write('INTENS INT_ERR GRAD RAD RMSRES FOURSL ITER NUM RESID_1 RESID_2 RESID_3 '+ \
           'RESID_4 ECC POSANG X0 Y0 FOUR_2 THIRD_2\n')
cmd='cat tmp.tmp tmp2.prf | xml_archangel -a '+prefix+' prf'
print cmd
os.system(cmd)
os.remove('tmp.tmp')
os.remove('tmp.prf')
os.remove('tmp2.prf')
