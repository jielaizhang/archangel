#!/usr/bin/env python

import sys, os

if '-h' in sys.argv:
  print 'line_up_dots file'
  print
  print 'finds decimal points and lines them up, integers right just'
  sys.exit()

lines=[tmp[:-1] for tmp in open(sys.argv[1],'r').readlines()]

front=[] ; back=[]
for x in lines[0].split():
  if '.' not in x:
    front.append(len(x))
    back.append(0)
  else:
    front.append(len(x.split('.')[0]))
    back.append(len(x.split('.')[1]))

for line in lines[1:]:
  for n,x in enumerate(line.split()):
    if '.' not in x:
      if len(x) > front[n]: front[n]=len(x)
    else:
      if len(x.split('.')[0]) > front[n]: front[n]=len(x.split('.')[0])
      if len(x.split('.')[1]) > back[n]: back[n]=len(x.split('.')[1])

for line in lines:
  for n,x in enumerate(line.split()):
    if back[n] == 0:
      print x.rjust(front[n]),
    else:
      print x.split('.')[0].rjust(front[n])+'.'+x.split('.')[1].ljust(back[n]),
  print
