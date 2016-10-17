#!/usr/bin/env python

def remove_strange(x):
  kill=[]
  for z in x:
    if ord(z) < 10 or ord(z) > 126: kill.append(z)
  for z in kill:
    x=x.replace(z,'')

  x=x.replace('&amp; ',' ')

  while 1:
    if '&amp;' not in x: break
    i1=x.index('&amp;')
    t=x[i1:].index(';')+i1
    i2=x[t+1:].index(';')+t
    x=x[:i1]+x[i2+2:]

  return x

if __name__ == "__main__":

  while 1:
    try:
      tmp=raw_input()
    except:
      break
    print remove_strange(tmp)
