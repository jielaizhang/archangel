#!/usr/bin/env python

import socket,time

print 'starting socket'
mySocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print 'binding'
mySocket.bind(('',6331))
print 'listen'
mySocket.listen(1)
channel, details=mySocket.accept()
print 'We have opened a connection with', details
while True:
  data=channel.recv(100)
  if data == 'exit':
    print 'got exit'
    break
  print 'socket1 got',data
  print 'socket1 sending','socket1 '+data
  channel.send('socket1 '+data)
channel.close()
