#!/usr/bin/env python

import subprocess, sys, os

home=os.environ['ARCHANGEL_HOME']

try:
  import pylab
  cmd=[home+'/util/probe.py']+sys.argv[1:]
except:
  cmd=[home+'/util/probe_x11.py']+sys.argv[1:]
devnull = file ("/dev/null", "r+")
subprocess.Popen(cmd, stderr=devnull)
