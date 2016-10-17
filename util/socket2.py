#!/usr/bin/env python

import socket
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#mySocket.connect(('localhost',6331))
mySocket.connect(('deepcore.uoregon.edu',6331))
while 1:
  line=raw_input()
  if line == '/': break
  print 'socket2 sending',line
  mySocket.send(line)
  print 'socket2 got back',mySocket.recv(100)
mySocket.close()
