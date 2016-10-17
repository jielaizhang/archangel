#!/usr/bin/env python

import sys,os

if '-h' in sys.argv:
  print 'peak filename x1,x2,y1,y2 threshold'
  print
  print 'find all the peaks above threshold intensity'
  print 'if x1,x2,y1,y2 do sub-raster'
  sys.exit()

#print 'threshold '+sys.argv[1]+' '+sys.argv[2]+' '+sys.argv[-1]+' > thres.tmp'
os.system('threshold '+sys.argv[1]+' '+sys.argv[2]+' '+sys.argv[-1]+' > thres.tmp')
#print 'find_peaks '+sys.argv[1]
thres=os.popen('find_peaks '+sys.argv[1]).read().split('\n')

#if ',' in sys.argv[2]:
#  x1=float(sys.argv[2].split(',')[0])
#  x2=float(sys.argv[2].split(',')[1])
#  y1=float(sys.argv[2].split(',')[2])
#  y2=float(sys.argv[2].split(',')[3])
#else:
#  x1=0. ; x2=1.e33 ; y1=0. ; y2=1.e33
#
#for z in thres[:-1]:
#  if x1 < float(z.split()[0]) and float(z.split()[0]) < x2 and \
#     y1 < float(z.split()[1]) and float(z.split()[0]) < y2:
#       print z

for z in thres[:-1]: print z
