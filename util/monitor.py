#!/usr/bin/env python

import os, sys, time

os.system('clear')
lastdata=[]
data=[tmp for tmp in open(sys.argv[-1],'r').readlines()]
#ilength=int(data[0])
header=data[1]
istart=1
while 1:
  time.sleep(0.5)
  data=[tmp for tmp in open(sys.argv[-1],'r').readlines()]
  if data != lastdata:
    os.system('clear')
#    if len(data) > ilength:
#      if istart != len(data)-ilength:
#        istart=len(data)-ilength
#        os.system('clear')
#    else:
#      istart=1
    os.system('tput cup 0 0')
    if 'no header' not in header: print header,
    for z in data[istart+1:]:
      print z,
#    if len(data) > ilength: print header,
    lastdata=data
