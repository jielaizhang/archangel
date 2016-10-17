#!/usr/bin/env python

import sys

if sys.argv[1].find('-')==0:
  for n in (range(int(sys.argv[1][1:]))):  
    try:
      print raw_input()
    except EOFError:
      break
elif sys.argv[1].find('-')==len(sys.argv[1])-1:
  for n in (range(int(sys.argv[1][:-1])-1)):
    try:
      raw_input()
    except EOFError:
      break
  while 1:
    try:
      print raw_input()
    except EOFError:
      break
elif sys.argv[1].find('-')>0:
  x=int(sys.argv[1].find('-'))
  start=int(sys.argv[1][:x])
  stop=int(sys.argv[1][x+1:])-start+1
  for n in range(start):
    line=raw_input()
  for n in range(stop):
    try:
      print raw_input()
    except EOFError:
      break
else:
  for n in (range(int(sys.argv[1]))):
    line=raw_input()
    if not line: break
  try:
    print raw_input()
  except EOFError:
    pass
