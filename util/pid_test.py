#!/usr/bin/env python

import os,subprocess, signal

p=subprocess.Popen('/usr/local/bin/rxvt -fn 6x13 -bg black -fg white +sb -cr black -T "Probe Positions" \
                     -geometry 150x25+100+50 -e '+os.environ['ARCHANGEL_HOME']+'/util/monitor.py &',shell=True)

print p.pid

while True:
  try:
    tmp=raw_input()
  except:
    break
os.kill(p.pid,signal.SIGKILL)
os.kill(p.pid+1,signal.SIGKILL)
