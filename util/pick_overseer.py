#!/usr/bin/env python

import subprocess, sys, os

home=os.environ['ARCHANGEL_HOME']

if sys.argv[1] == '-v':
  icmd=2
else:
  icmd=1

try:
  import pylab
  cmd=[home+'/util/pick.py']+sys.argv[icmd:]
except:
  cmd=[home+'/util/pick_x11.py']+sys.argv[icmd:]

if sys.argv[1] == '-v':
  subprocess.Popen(cmd)
else:
  devnull = file ("/dev/null", "r+")
  subprocess.Popen(cmd, stderr=devnull)
