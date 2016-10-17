#!/usr/bin/env python

import subprocess, os

def kill_pids(pids,kill_all):
  tmp=[]
  for z in pids:
    try:
      if z[1] or kill_all:
        os.system('rm '+z[2])
        os.kill(z[0]+1,signal.SIGKILL) # god knows why the rxvt shell is pid+1, original shell is gone
      else:
        tmp.append(z)
    except:
      tmp.append(z)
  return tmp

pids=[]
file='out.tmp'
fout=open(file,'w')
fout.write('25\n')
print >> fout,'         x           y     '
fout.close()
p=subprocess.Popen('/Users/js/archangel/util/tterm.csh -x '+os.environ['ARCHANGEL_HOME']+'/util/monitor.py '+ \
                           file+' &',shell=True)
pids.append([p.pid,1,file])

while 1:
  tmp=raw_input()
  if not tmp: break
  fout=open(file,'a')
  fout.write(tmp+'\n')
  fout.close()

kill_pids(pids,1)
