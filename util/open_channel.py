#!/usr/bin/env python

import socket,os,time,subprocess,sys

p=subprocess.Popen(os.environ['ARCHANGEL_HOME']+'/util/socket_listbox.py -listbox -f '+sys.argv[-1]+' &',shell=True)
time.sleep(1)
channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
channel.connect(('localhost',2727))
print 'open channel'
channel.send('start')

while True:
  try:
    tmp=raw_input()
  except:
    break
  print 'sending',tmp
  channel.send(tmp)
  if tmp == 'quit': break

channel.close()
