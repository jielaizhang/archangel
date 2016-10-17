#!/usr/bin/env python

import subprocess, signal, sys, os

p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
out, err = p.communicate()
for line in out.splitlines():
  if sys.argv[-1] in line and 'kill' not in line:
    pid = int(line.split(None, 1)[0])
    os.system('kill -9 '+str(pid))
