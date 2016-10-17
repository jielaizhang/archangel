#!/usr/bin/env python

import subprocess, sys, os

home=os.environ['ARCHANGEL_HOME']

try:
  import pylab
  cmd=[home+'/sfb/bdd.py']+sys.argv[1:]
except:
  cmd=[home+'/sfb/bdd_x11.py']+sys.argv[1:]
devnull = file ("/dev/null", "r+")
subprocess.Popen(cmd, stderr=devnull)
