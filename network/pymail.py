#!/usr/bin/env python

import sys, os, smtplib

if len(sys.argv) < 1:
  id='your_email@address.com'
else:
  id=sys.argv[1]

file=open('mail.tmp','w')
file.write('To: '+id+'\nbcc: your_email@address.com\nSubject: ')
file.close()
os.system('/usr/local/bin/vim mail.tmp')
tmp=open('mail.tmp','r').readlines()
addr=[]
print 'Going to:'

for t in tmp:
  if 'Subject:' in t: break
  for x in t.replace('To:','').replace(' ','').replace('\n','').replace('bcc:','').replace('cc:','').split(','):
    if x:
      print ' ',x
      addr.append(x)

record=0
msg=''
for t in tmp:
  if 'cc:' in t or 'bcc:' in t or 'Subject:' in t: record=1
  if record: msg=msg+t

go=raw_input('Send? (y)/n: ')

if go != 'n':
  server=smtplib.SMTP('your_smtp_server.edu')
  server.sendmail('your_email@address.com',addr,msg)
  server.quit()
