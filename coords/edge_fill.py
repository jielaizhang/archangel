#!/usr/bin/env python

import sys, os, subprocess, os.path
import pyfits

if sys.argv[1] == '-h':
  print 'edge_fill file xc yc'
  print
  print 'finds edges of object at xc,yc, fills middle, writes marks to xml file'
  print
  print 'options: -xml = xml write'
  sys.exit()

fitsobj=pyfits.open(sys.argv[-3],"readonly")
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()

edge=[]
i=int(sys.argv[-2])-1
j=int(sys.argv[-1])-1
while 1:
  j=j+1
  if pix[j][i] != pix[j][i]: break
iend=i
jend=j-1
j=j-1
out='x y\n'
out=out+str(i+1)+' '+str(j+1)+'\n'
#print 'start',iend+1,jend+1
edge.append((i,j))

o=[(0,1),(1,0),(0,-1),(-1,0)]
direction=0
while 1:
  for w in range(4):
    z=w+direction
    if z > 3: z=z-4
#    print 'in',i+1,j+1,w,z,direction
    try:
      if pix[j+o[z][1]][i+o[z][0]] == pix[j+o[z][1]][i+o[z][0]]: break
    except:
      print 'i\'m lost',z,i+1,j+1
  direction=z-1
  if direction < 0: direction=3
  i=i+o[z][0]
  j=j+o[z][1]
  if i == iend and j == jend: break
  if (i,j) not in edge:
#    print i+1,j+1,z,direction
    edge.append((i,j))
    out=out+str(i+1)+' '+str(j+1)+'\n'

xmin=ymin=1.e33 ; xmax=ymax=-1.e33
for x,y in edge:
  if x < xmin: xmin=x
  if x > xmax: xmax=x
  if y < ymin: ymin=y
  if y > ymax: ymax=y

fill=[]
for j in range(ymin,ymax):
  x1=xmax
  for x,y in edge:
    if y == j:
      if x < x1: x1=x
  isw=1
  for i in range(x1,xmax):
    if (i,j) in edge: isw=1
    if pix[j][i] == pix[j][i]:
      if isw and (i,j) not in fill and (i,j) not in edge:
        out=out+str(i+1)+' '+str(j+1)+'\n'
        fill.append((i,j))
    else:
      if (i-1,j) in edge: isw=abs(isw-1)

if '-xml' in sys.argv:

  if not os.path.exists(sys.argv[-3]+'.xml'):
    os.system('xml_archangel -c '+sys.argv[-3]+' archangel')

  p=subprocess.Popen('xml_archangel -a '+sys.argv[-3].split('.')[0]+' marks', \
                      shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
  p.communicate(out[:-1])

else:

  for z in out.split('\n')[1:-1]:
    print z

